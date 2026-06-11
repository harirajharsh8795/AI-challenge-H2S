import src.patch_env
import os
import logging
from typing import Dict, List, Optional, Tuple, Any

from src.logger import PipelineLogger
from src.config import AppConfig, load_config
from src.feature_engineering import extract_candidate_skills
from src.utils import sanitize_text


# Retrieve pipeline-specific logger
logger = PipelineLogger.get_logger()

# Global singleton storage for loaded CrossEncoder model
_CROSS_ENCODER_SINGLETON: Optional[Any] = None


def load_cross_encoder(config: Optional[AppConfig] = None) -> Optional[Any]:
    """Loads the sentence-transformers CrossEncoder model dynamically.

    Uses 'cross-encoder/ms-marco-MiniLM-L-6-v2' by default, or loads the name
    from configuration, and falls back to None if package dependencies fail to load.

    Args:
        config (Optional[AppConfig]): Pipeline configuration object.

    Returns:
        Optional[CrossEncoder]: Loaded model instance, or None if load fails.
    """
    global _CROSS_ENCODER_SINGLETON
    if _CROSS_ENCODER_SINGLETON is not None:
        return _CROSS_ENCODER_SINGLETON

    model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    device = "cpu"

    if config is not None:
        try:
            if hasattr(config, "models") and config.models:
                if hasattr(config.models, "cross_encoder_model"):
                    model_name = config.models.cross_encoder_model
                device = getattr(config.models, "device", "cpu")
        except Exception as e:
            logger.warning(
                "Could not read cross-encoder details from config: %s. Using default model '%s'.",
                str(e),
                model_name,
            )

    # Force compute device to cpu to satisfy resource constraints
    device = "cpu"

    # Resolve local path if present in root/models/ms-marco-MiniLM-L-6-v2
    local_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "ms-marco-MiniLM-L-6-v2")
    if os.path.exists(local_path):
        model_load_path = local_path
        logger.info("Local CrossEncoder model directory found at '%s'. Loading offline.", local_path)
    else:
        model_load_path = model_name

    try:
        from sentence_transformers import CrossEncoder
        logger.info("Loading sentence-transformers CrossEncoder '%s' on %s...", model_load_path, device)
        _CROSS_ENCODER_SINGLETON = CrossEncoder(model_load_path, device=device)
        logger.info("CrossEncoder model successfully initialized.")
        return _CROSS_ENCODER_SINGLETON
    except Exception as e:
        logger.error(
            "Failed to load sentence-transformers CrossEncoder model '%s': %s. "
            "Reranking will continue using fallback semantic scoring.",
            model_load_path,
            str(e),
        )
        return None



def build_candidate_text(candidate: Dict) -> str:
    """Assembles candidate metadata fields into a structured text document.

    Combines: current title, headline, summary, skills, and career history.

    Args:
        candidate (Dict): The candidate record dictionary.

    Returns:
        str: Sanitized, lowercase space-separated candidate text.
    """
    if not isinstance(candidate, dict):
        logger.warning("Non-dictionary candidate passed to build_candidate_text. Returning empty string.")
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


def score_candidate_pairs(
    model: Optional[Any],
    pairs: List[Tuple[str, str]],
    batch_size: int = 32
) -> Optional[List[float]]:
    """Predicts scores for (query, document) pairs using the CrossEncoder.

    Args:
        model (Optional[CrossEncoder]): The loaded CrossEncoder model.
        pairs (List[Tuple[str, str]]): List of tuples where each tuple contains (jd_text, candidate_text).
        batch_size (int): Size of batches to feed to the model.

    Returns:
        Optional[List[float]]: List of predicted float scores, or None if prediction fails.
    """
    if model is None or not pairs:
        return None

    try:
        # CrossEncoder.predict returns ndarray of float32
        scores = model.predict(pairs, batch_size=batch_size, show_progress_bar=False)
        return [float(score) for score in scores]
    except Exception as e:
        logger.error("Failed to predict scores using CrossEncoder: %s. Returning None.", str(e))
        return None


def rerank_candidates(
    candidates: List[Dict],
    jd_text: str,
    top_k: int = 100,
    config: Optional[AppConfig] = None
) -> Tuple[List[Dict], Dict]:
    """Scores candidate records against the job description using a Cross-Encoder.

    Takes the top_k candidates, computes cross encoder scores for them, and returns
    the reranked candidates along with metadata containing individual scores.

    Args:
        candidates (List[Dict]): Pre-filtered candidate list (typically from Stage 2).
        jd_text (str): Job description raw text query.
        top_k (int): Number of top candidates to rerank (default: 100).
        config (Optional[AppConfig]): Pipeline configuration object.

    Returns:
        Tuple[List[Dict], Dict]: A tuple of:
            - List[Dict]: Cross-encoder reranked candidate list.
            - Dict: Metadata containing "scores" map and stats.
    """
    total = len(candidates)
    if total == 0:
        logger.warning("Empty candidate list provided to rerank_candidates. Returning empty results.")
        return [], {"scores": {}, "statistics": {"processed": 0}}

    # Load configuration if not provided
    if config is None:
        try:
            config = load_config()
        except Exception as e:
            logger.warning("Could not load configuration inside cross-encoder reranker: %s", str(e))

    # Slice the candidates to only rerank the top_k (e.g. 100-150)
    rerank_limit = max(1, min(total, top_k))
    candidates_to_rerank = candidates[:rerank_limit]
    remaining_candidates = candidates[rerank_limit:]

    model = load_cross_encoder(config)

    # Build pairs of (jd_text, candidate_text)
    sanitized_jd = sanitize_text(jd_text)
    pairs = []
    for cand in candidates_to_rerank:
        cand_text = build_candidate_text(cand)
        pairs.append((sanitized_jd, cand_text))

    scores = score_candidate_pairs(model, pairs)

    # Graceful fallback: Use simple token overlap scoring if cross-encoder is unavailable
    if scores is None or len(scores) != len(candidates_to_rerank):
        logger.warning(
            "CrossEncoder scoring failed or model unavailable. Executing fallback word-overlap semantic scoring."
        )
        scores = []
        jd_words = set(sanitized_jd.split())

        for _, cand_text in pairs:
            cand_words = set(cand_text.split())
            if not jd_words or not cand_words:
                overlap = 0.0
            else:
                overlap = len(cand_words.intersection(jd_words)) / len(jd_words)
            scores.append(overlap)

    # Match scores to candidates
    scored_candidates = []
    for cand, score in zip(candidates_to_rerank, scores):
        scored_candidates.append((score, cand))

    # Sort key: 1. Score descending, 2. candidate_id ascending (deterministic tie-breaking)
    def sort_key(item: Tuple[float, Dict]) -> Tuple[float, str]:
        score_val, cand_record = item
        cand_id = cand_record.get("candidate_id", "")
        return (-score_val, str(cand_id))

    scored_candidates.sort(key=sort_key)

    # Construct final ranked list and assign ranks
    ranked_candidates = []
    metadata_scores = {}
    ranked_meta_list = []

    for idx, (score, cand) in enumerate(scored_candidates):
        rank = idx + 1
        cand_id = cand.get("candidate_id")

        # Copy candidate record to inject stage-specific metadata
        cand_copy = dict(cand)
        cand_copy["cross_encoder_score"] = float(score)
        cand_copy["rank"] = rank
        ranked_candidates.append(cand_copy)

        if cand_id is not None:
            metadata_scores[cand_id] = {
                "cross_encoder_score": float(score),
                "rank": rank
            }
            ranked_meta_list.append({
                "candidate_id": cand_id,
                "cross_encoder_score": float(score),
                "rank": rank
            })

    # For any remaining candidates that were NOT in the top_k, we append them in their
    # original order with default/low fallback scores to maintain list integrity
    for idx, cand in enumerate(remaining_candidates):
        rank = rerank_limit + idx + 1
        cand_id = cand.get("candidate_id")
        cand_copy = dict(cand)
        cand_copy["cross_encoder_score"] = -1.0  # Safe default score for unscored candidates
        cand_copy["rank"] = rank
        ranked_candidates.append(cand_copy)

        if cand_id is not None:
            metadata_scores[cand_id] = {
                "cross_encoder_score": -1.0,
                "rank": rank
            }
            ranked_meta_list.append({
                "candidate_id": cand_id,
                "cross_encoder_score": -1.0,
                "rank": rank
            })

    metadata = {
        "scores": metadata_scores,
        "ranked_list": ranked_meta_list,
        "statistics": {
            "total_input_candidates": total,
            "reranked_count": len(candidates_to_rerank),
            "unscored_count": len(remaining_candidates)
        }
    }

    logger.info("Successfully reranked top %d candidates using CrossEncoder.", len(candidates_to_rerank))
    return ranked_candidates, metadata
