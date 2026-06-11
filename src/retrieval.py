from typing import Dict, List, Optional, Tuple
from rank_bm25 import BM25Okapi
from src.logger import PipelineLogger
from src.config import AppConfig, load_config
from src.honeypots import is_honeypot, is_consulting_only
from src.feature_engineering import extract_candidate_skills
from src.utils import sanitize_text

logger = PipelineLogger.get_logger()


def build_candidate_document(candidate: Dict) -> str:
    """Creates a unified, clean, searchable text document for indexing.

    Combines the candidate's headline, professional summary, extracted skills,
    career experience titles and descriptions, and company names.

    Args:
        candidate (Dict): The candidate record dictionary.

    Returns:
        str: Sanitized, lowercase space-separated document text.
    """
    if not isinstance(candidate, dict):
        logger.warning("Non-dictionary candidate passed to build_candidate_document. Returning empty string.")
        return ""

    profile = candidate.get("profile", {})
    if not isinstance(profile, dict):
        profile = {}

    # Extract headline and summary
    headline = profile.get("headline", "")
    summary = profile.get("summary", "")

    # Extract skills using the robust feature engineering utility
    skills_list = extract_candidate_skills(candidate)
    skills_text = " ".join(skills_list)

    # Extract experience details and company names from career history
    career_history = candidate.get("career_history", [])
    career_parts = []
    company_names = []

    if isinstance(career_history, list):
        for job in career_history:
            if isinstance(job, dict):
                title = job.get("title", "")
                company = job.get("company", "")
                description = job.get("description", "")

                if company:
                    company_names.append(company)
                if title or description:
                    career_parts.append(f"{title} {description}")

    career_text = " ".join(career_parts)
    companies_text = " ".join(company_names)

    # Combine years of experience and current title
    y_exp = profile.get("years_of_experience", "")
    curr_title = profile.get("current_title", "")
    experience_summary = f"{curr_title} {y_exp} years"

    # Assemble complete searchable text representation
    full_text = f"{headline} {summary} {skills_text} {experience_summary} {career_text} {companies_text}"

    return sanitize_text(full_text)


def build_bm25_index(candidates: List[Dict]) -> Optional[BM25Okapi]:
    """Generates a BM25 Okapi index over a list of candidate profiles.

    Avoids unnecessary corpus retention by tokenizing documents directly.

    Args:
        candidates (List[Dict]): Pre-filtered candidate records.

    Returns:
        Optional[BM25Okapi]: Built BM25 index object, or None if candidates list is empty.
    """
    if not candidates:
        logger.warning("Empty candidate list passed to build_bm25_index. BM25 index will not be built.")
        return None

    logger.info("Building BM25 index over %d candidate profiles...", len(candidates))
    
    # Tokenize corpus directly to minimize memory retention of raw document strings
    try:
        tokenized_corpus = [build_candidate_document(cand).split() for cand in candidates]
        index = BM25Okapi(tokenized_corpus)
        logger.info("BM25 index successfully generated.")
        return index
    except Exception as e:
        logger.exception("Unexpected error building BM25 index: %s", str(e))
        return None


def apply_hard_filters(
    candidate: Dict,
    config: Optional[AppConfig] = None,
    jd_spec: Optional[Dict] = None,
) -> bool:
    """Evaluates hard filters on a single candidate to verify search viability.

    Filters candidates based on:
    - Honeypot profile anomalies
    - Consulting-only employer history
    - Experience boundaries (resolved in priority order: JD Spec -> Config -> Default)

    Args:
        candidate (Dict): The candidate record dictionary.
        config (Optional[AppConfig]): Pipeline configuration object.
        jd_spec (Optional[Dict]): Structured job description specifications.

    Returns:
        bool: True if candidate passes all filters, False otherwise.

    Raises:
        ValueError: If pipeline current reference date is not available in configuration.
    """
    if not isinstance(candidate, dict):
        return False

    cand_id = candidate.get("candidate_id", "UNKNOWN")

    # Load configuration if not provided
    if config is None:
        try:
            config = load_config()
        except Exception as e:
            logger.warning("Could not load configuration inside apply_hard_filters. Using defaults: %s", str(e))

    # 1. Honeypot check (Requires pipeline current date, no hardcoded fallbacks allowed)
    if config and hasattr(config, "pipeline") and config.pipeline and config.pipeline.current_date:
        current_date = config.pipeline.current_date
    else:
        raise ValueError(
            "Configuration pipeline.current_date is required for honeypot checking and must be supplied."
        )

    if is_honeypot(candidate, current_date):
        logger.debug("Candidate %s filtered out: Triggered honeypot detection.", str(cand_id))
        return False

    # 2. Consulting-only employer check
    if is_consulting_only(candidate):
        logger.debug("Candidate %s filtered out: Stated history is consulting-only.", str(cand_id))
        return False

    # 3. Years of experience range filtering
    profile = candidate.get("profile", {})
    if not isinstance(profile, dict):
        profile = {}

    y_exp = profile.get("years_of_experience")
    if y_exp is None:
        logger.debug("Candidate %s filtered out: Missing years_of_experience.", str(cand_id))
        return False

    try:
        y_exp_val = float(y_exp)
    except (ValueError, TypeError):
        logger.warning("Candidate %s contains non-numeric experience value: %s. Filtering out.", str(cand_id), str(y_exp))
        return False

    # Resolve experience limits by priority: JD Spec -> Config -> Default (3.0 to 12.0)
    min_exp = None
    max_exp = None

    # Priority 1: JD Spec
    if isinstance(jd_spec, dict):
        exp_range = jd_spec.get("experience_range")
        if isinstance(exp_range, dict):
            min_exp = exp_range.get("min_years")
            max_exp = exp_range.get("max_years")

    # Priority 2: Config
    if min_exp is None or max_exp is None:
        if config and hasattr(config, "retrieval") and config.retrieval:
            if min_exp is None:
                min_exp = getattr(config.retrieval, "min_experience_years", None)
            if max_exp is None:
                max_exp = getattr(config.retrieval, "max_experience_years", None)

    # Priority 3: Default
    if min_exp is None:
        min_exp = 3.0
    if max_exp is None:
        max_exp = 12.0

    if y_exp_val < min_exp or y_exp_val > max_exp:
        logger.debug(
            "Candidate %s filtered out: Experience %.1f outside retrieval limits [%.1f, %.1f].",
            str(cand_id),
            y_exp_val,
            min_exp,
            max_exp,
        )
        return False

    return True


def compute_weighted_skill_boost(candidate: Dict, jd_spec: Dict) -> float:
    """Computes a weighted skill match boost score for a candidate.

    Assigns weight 3.0 for matching must-have skills, and 1.0 for preferred skills.

    Args:
        candidate (Dict): The candidate record dictionary.
        jd_spec (Dict): Structured job description specifications.

    Returns:
        float: Total weighted skill boost score.
    """
    if not isinstance(candidate, dict) or not isinstance(jd_spec, dict):
        return 0.0

    cand_skills = set(extract_candidate_skills(candidate))
    must_have = jd_spec.get("must_have", [])
    preferred = jd_spec.get("preferred", [])

    boost = 0.0

    if isinstance(must_have, list):
        for skill in must_have:
            if isinstance(skill, str) and skill.lower().strip() in cand_skills:
                boost += 3.0

    if isinstance(preferred, list):
        for skill in preferred:
            if isinstance(skill, str) and skill.lower().strip() in cand_skills:
                boost += 1.0

    return boost


def retrieve_top_candidates(
    query: str,
    candidates: List[Dict],
    top_k: int = 2000,
    config: Optional[AppConfig] = None,
    jd_spec: Optional[Dict] = None,
) -> Tuple[List[Dict], Dict]:
    """Applies hard filters and ranks remaining candidates using BM25 with weighted skill boosting.

    Args:
        query (str): Job description text query.
        candidates (List[Dict]): Raw list of candidate records.
        top_k (int): Number of candidates to retrieve.
        config (Optional[AppConfig]): Pipeline configuration object.
        jd_spec (Optional[Dict]): Structured job description specifications.

    Returns:
        Tuple[List[Dict], Dict]: A tuple containing:
            1. List[Dict]: Top ranked candidate dictionaries list.
            2. Dict: Retrieval metadata and scores for downstream ranking.
    """
    total_candidates = len(candidates)
    if total_candidates == 0:
        logger.warning("Empty candidates list provided to retrieve_top_candidates. Returning empty results.")
        empty_metadata = {
            "statistics": {
                "total_candidates": 0,
                "filtered_candidates": 0,
                "retrieved_candidates": 0
            },
            "scores": {}
        }
        return [], empty_metadata

    # 1. Load config if not provided
    if config is None:
        try:
            config = load_config()
        except Exception as e:
            logger.warning("Could not load configuration inside retrieve_top_candidates: %s", str(e))

    # 2. Filter candidates using hard filters
    filtered_candidates = []
    for cand in candidates:
        try:
            if apply_hard_filters(cand, config, jd_spec):
                filtered_candidates.append(cand)
        except Exception as e:
            logger.warning(
                "Error applying hard filters on candidate %s: %s. Candidate excluded.",
                str(cand.get("candidate_id", "UNKNOWN")),
                str(e)
            )

    filtered_count = len(filtered_candidates)
    logger.info(
        "Candidate filtering complete. Passed filters: %d/%d candidates.",
        filtered_count,
        total_candidates,
    )

    if not filtered_candidates:
        empty_metadata = {
            "statistics": {
                "total_candidates": total_candidates,
                "filtered_candidates": 0,
                "retrieved_candidates": 0
            },
            "scores": {}
        }
        return [], empty_metadata

    # 3. Build BM25 index over filtered corpus
    bm25 = build_bm25_index(filtered_candidates)
    
    # 4. Tokenize search query (no duplications, standard BM25 match)
    query_tokens = []
    if query:
        sanitized_query = sanitize_text(query)
        query_tokens.extend(sanitized_query.split())

    # Calculate BM25 scores
    if bm25 is not None and query_tokens:
        try:
            bm25_scores = bm25.get_scores(query_tokens)
        except Exception as e:
            logger.exception("Error during BM25 score calculation: %s. Defaulting BM25 scores to 0.0.", str(e))
            bm25_scores = [0.0] * filtered_count
    else:
        bm25_scores = [0.0] * filtered_count

    # 5. Apply weighted skill boosting and compile metadata
    scored_candidates = []
    candidate_scores_meta = {}

    for cand, base_bm25 in zip(filtered_candidates, bm25_scores):
        cand_id = cand.get("candidate_id")
        
        # Calculate skill boost
        skill_boost = 0.0
        if jd_spec:
            skill_boost = compute_weighted_skill_boost(cand, jd_spec)

        # Final ranked relevance score
        final_retrieval_score = float(base_bm25 + skill_boost)
        scored_candidates.append((final_retrieval_score, cand))

        if cand_id is not None:
            candidate_scores_meta[cand_id] = {
                "bm25_score": float(base_bm25),
                "skill_boost": float(skill_boost),
                "retrieval_score": final_retrieval_score
            }

    # Sort key: 1. Score descending, 2. candidate_id ascending (deterministic tie-breaking)
    def sort_key(item):
        score, cand = item
        cand_id = cand.get("candidate_id", "")
        return (-score, str(cand_id))

    scored_candidates.sort(key=sort_key)

    # Extract top_k candidates
    ranked_candidates = [cand for _, cand in scored_candidates[:top_k]]
    retrieved_count = len(ranked_candidates)

    metadata = {
        "statistics": {
            "total_candidates": total_candidates,
            "filtered_candidates": filtered_count,
            "retrieved_candidates": retrieved_count
        },
        "scores": candidate_scores_meta
    }

    logger.info("Successfully retrieved top %d candidates.", retrieved_count)
    return ranked_candidates, metadata
