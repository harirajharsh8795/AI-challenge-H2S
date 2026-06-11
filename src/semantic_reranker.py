import src.patch_env
import os
import numpy as np
from typing import Dict, List, Optional, Tuple

from src.logger import PipelineLogger
from src.config import AppConfig, load_config
from src.feature_engineering import extract_candidate_skills
from src.utils import sanitize_text


logger = PipelineLogger.get_logger()

# Global singleton storage for loaded embedding model to prevent redundant re-loading
_MODEL_SINGLETON = None


def load_embedding_model(config: Optional[AppConfig] = None) -> Optional[object]:
    """Loads the sentence-transformers model dynamically.

    Uses 'all-MiniLM-L6-v2' and falls back to None if package dependencies
    (e.g., PyTorch, sentence-transformers) fail to load or throw recursion errors.

    Args:
        config (Optional[AppConfig]): Pipeline configuration object.

    Returns:
        Optional[SentenceTransformer]: Loaded model instance, or None if load fails.
    """
    global _MODEL_SINGLETON
    if _MODEL_SINGLETON is not None:
        return _MODEL_SINGLETON

    model_name = "all-MiniLM-L6-v2"
    device = "cpu"

    if config is not None:
        try:
            if hasattr(config, "models") and config.models:
                # Handle potential naming differences in configs
                if hasattr(config.models, "embedding_model"):
                    model_name = config.models.embedding_model
                elif hasattr(config.models, "dense_embedding_model"):
                    model_name = config.models.dense_embedding_model
                device = getattr(config.models, "device", "cpu")
        except Exception as e:
            logger.warning("Could not read embedding model details from config: %s. Using default model '%s'.", str(e), model_name)

    # Force compute device to cpu to satisfy resource constraints
    device = "cpu"

    # Resolve local path if present in root/models/all-MiniLM-L6-v2
    local_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "all-MiniLM-L6-v2")
    if os.path.exists(local_path):
        model_load_path = local_path
        logger.info("Local embedding model directory found at '%s'. Loading offline.", local_path)
    else:
        model_load_path = model_name

    try:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading sentence-transformers model '%s' on %s...", model_load_path, device)
        _MODEL_SINGLETON = SentenceTransformer(model_load_path, device=device)
        logger.info("Embedding model successfully initialized.")
        return _MODEL_SINGLETON
    except Exception as e:
        logger.error(
            "Failed to load sentence-transformers model '%s': %s. "
            "Reranking will continue using fallback semantic scoring.",
            model_load_path,
            str(e),
        )
        return None



def build_candidate_embedding_text(candidate: Dict) -> str:
    """Assembles candidate metadata fields into a structured text document.

    Combines: current title, headline, summary, skills, and career history.

    Args:
        candidate (Dict): The candidate record dictionary.

    Returns:
        str: Sanitized, lowercase space-separated candidate text.
    """
    if not isinstance(candidate, dict):
        logger.warning("Non-dictionary candidate passed to build_candidate_embedding_text. Returning empty string.")
        return ""

    profile = candidate.get("profile", {})
    if not isinstance(profile, dict):
        profile = {}

    headline = profile.get("headline", "")
    summary = profile.get("summary", "")
    current_title = profile.get("current_title", "")

    # Extract skills list and format as a comma-separated list
    skills_list = extract_candidate_skills(candidate)
    skills_text = ", ".join(skills_list)

    # Extract career history descriptions
    career_history = candidate.get("career_history", [])
    career_parts = []

    if isinstance(career_history, list):
        for job in career_history:
            if isinstance(job, dict):
                title = job.get("title", "")
                company = job.get("company", "")
                desc = job.get("description", "")
                
                job_desc = f"{title} at {company}"
                if desc:
                    job_desc += f": {desc}"
                career_parts.append(job_desc)

    career_text = " ".join(career_parts)

    # Compile structured representation
    full_text = f"Title: {current_title}. Headline: {headline}. Summary: {summary}. Skills: {skills_text}. Experience: {career_text}."

    return sanitize_text(full_text)


def generate_embeddings(texts: List[str], model: Optional[object]) -> Optional[np.ndarray]:
    """Generates dense embedding vectors for a list of texts.

    Supports batch mode and forces CPU cache optimizations.

    Args:
        texts (List[str]): Input texts to embed.
        model (Optional[SentenceTransformer]): Loaded sentence-transformers model.

    Returns:
        Optional[np.ndarray]: A 2D numpy array of shape (N, D) containing embeddings,
                              or None if model is unavailable or generation fails.
    """
    if model is None:
        return None

    if not texts:
        # Get embedding dimension dynamically
        try:
            dim = model.get_sentence_embedding_dimension()
        except Exception:
            dim = 384
        return np.empty((0, dim))

    try:
        # normalize_embeddings=True optimizes cosine similarity to dot product
        embeddings = model.encode(
            texts,
            batch_size=64,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embeddings
    except Exception as e:
        logger.error("Failed to generate dense embeddings: %s. Returning None.", str(e))
        return None


def compute_semantic_similarity(
    candidate_embeddings: Optional[np.ndarray],
    jd_embedding: Optional[np.ndarray]
) -> np.ndarray:
    """Computes cosine similarity between candidate embeddings and job description.

    Args:
        candidate_embeddings (Optional[np.ndarray]): 2D array of candidate embeddings.
        jd_embedding (Optional[np.ndarray]): Job description embedding vector.

    Returns:
        np.ndarray: A 1D array of floats containing similarity scores.
    """
    if candidate_embeddings is None or jd_embedding is None:
        return np.array([])

    if candidate_embeddings.size == 0 or jd_embedding.size == 0:
        return np.array([])

    # Ensure JD vector is a 1D array
    if jd_embedding.ndim == 2 and jd_embedding.shape[0] == 1:
        jd_vec = jd_embedding[0]
    elif jd_embedding.ndim == 1:
        jd_vec = jd_embedding
    else:
        # Fallback flattening
        jd_vec = jd_embedding.flatten()

    # Normalize JD vector defensively
    jd_norm = np.linalg.norm(jd_vec)
    if jd_norm > 1e-9:
        jd_vec = jd_vec / jd_norm

    # Normalize candidate embeddings defensively
    cand_norms = np.linalg.norm(candidate_embeddings, axis=1, keepdims=True)
    cand_norms = np.where(cand_norms > 1e-9, cand_norms, 1.0)
    cand_normed = candidate_embeddings / cand_norms

    # Cosine similarity is equivalent to dot product on normalized vectors
    scores = np.dot(cand_normed, jd_vec)
    return scores


def rerank_candidates(
    candidates: List[Dict],
    jd_text: str,
    top_k: int = 500,
    config: Optional[AppConfig] = None
) -> Tuple[List[Dict], Dict]:
    """Scores candidate records against the job description using dense representations.

    Ranks candidates in descending order of similarity, falling back gracefully
    to token-overlap semantic similarity if dense models cannot be loaded.

    Args:
        candidates (List[Dict]): Pre-filtered List of candidate profiles.
        jd_text (str): Job description raw text query.
        top_k (int): Number of top reranked candidates to return.
        config (Optional[AppConfig]): Pipeline configuration object.

    Returns:
        Tuple[List[Dict], Dict]: A tuple containing:
            1. List[Dict]: Semantic reranked candidate list.
            2. Dict: Metadata dictionary mapping candidate_id to semantic_score.
    """
    total = len(candidates)
    if total == 0:
        logger.warning("Empty candidate list provided to rerank_candidates. Returning empty results.")
        return [], {"scores": {}}

    # Load configuration if not provided
    if config is None:
        try:
            config = load_config()
        except Exception as e:
            logger.warning("Could not load configuration inside rerank_candidates: %s", str(e))

    # Load embedding model
    model = load_embedding_model(config)

    # 1. Build candidate structured texts
    texts = [build_candidate_embedding_text(cand) for cand in candidates]

    # 2. Generate embeddings
    cand_embeddings = generate_embeddings(texts, model)
    jd_embedding = None
    if model is not None and jd_text:
        jd_embedding = generate_embeddings([jd_text], model)

    # 3. Compute semantic similarity scores
    if cand_embeddings is not None and jd_embedding is not None:
        try:
            scores = compute_semantic_similarity(cand_embeddings, jd_embedding)
        except Exception as e:
            logger.exception("Error during similarity calculation: %s. Using fallback score.", str(e))
            scores = None
    else:
        scores = None

    # Graceful fallback: Normalized token-overlap semantic scoring
    if scores is None or len(scores) != total:
        logger.warning("Dense similarity unavailable. Executing fallback word-overlap semantic scoring.")
        scores_list = []
        jd_words = set(sanitize_text(jd_text).split())
        
        for text in texts:
            cand_words = set(text.split())
            if not jd_words or not cand_words:
                overlap = 0.0
            else:
                overlap = len(cand_words.intersection(jd_words)) / len(jd_words)
            scores_list.append(overlap)
        scores = np.array(scores_list)

    # 4. Pair scores with candidates and sort deterministically
    scored_candidates = []
    metadata_scores = {}

    for cand, score in zip(candidates, scores):
        cand_id = cand.get("candidate_id")
        score_val = float(score)
        scored_candidates.append((score_val, cand))
        
        if cand_id is not None:
            metadata_scores[cand_id] = score_val

    # Sort key: 1. Score descending, 2. candidate_id ascending (string format)
    def sort_key(item):
        score_val, cand = item
        cand_id = cand.get("candidate_id", "")
        return (-score_val, str(cand_id))

    scored_candidates.sort(key=sort_key)

    # Extract top_k results
    ranked_candidates = [cand for _, cand in scored_candidates[:top_k]]
    metadata = {"scores": metadata_scores}

    logger.info("Successfully reranked and retrieved top %d candidates.", len(ranked_candidates))
    return ranked_candidates, metadata
