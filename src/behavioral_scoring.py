from datetime import date
from typing import Dict, List, Optional, Tuple
from src.logger import PipelineLogger
from src.config import AppConfig, load_config
from src.utils import parse_date, get_elapsed_days
from src.feature_engineering import build_feature_vector, compute_location_score
from src.honeypots import is_consulting_only

logger = PipelineLogger.get_logger()


def get_reference_date(config: Optional[AppConfig] = None) -> date:
    """Resolves the reference date following the priority chain:

    Config Date -> Runtime Current Date -> Safe Fallback Date.

    Args:
        config (Optional[AppConfig]): Pipeline configuration object.

    Returns:
        date: Reference date for calculations.
    """
    # 1. Config Date
    if config and hasattr(config, "pipeline") and config.pipeline:
        cfg_date = getattr(config.pipeline, "current_date", None)
        if cfg_date:
            if isinstance(cfg_date, date):
                return cfg_date
            parsed = parse_date(str(cfg_date))
            if parsed:
                return parsed

    # 2. Runtime Current Date
    try:
        return date.today()
    except Exception as e:
        logger.warning("Could not fetch date.today() runtime date: %s", str(e))

    # 3. Safe Fallback Date
    return date(2026, 6, 4)


def compute_response_rate_score(candidate: Dict) -> float:
    """Calculates a normalized score (0.0 to 1.0) for recruiter response rate.

    Args:
        candidate (Dict): The candidate record dictionary.

    Returns:
        float: Response rate score.
    """
    if not isinstance(candidate, dict):
        return 0.0

    signals = candidate.get("redrob_signals", {})
    if not isinstance(signals, dict):
        return 0.0

    val = signals.get("recruiter_response_rate", 0.0)
    try:
        return max(0.0, min(1.0, float(val)))
    except (ValueError, TypeError):
        return 0.0


def compute_activity_score(candidate: Dict, config: Optional[AppConfig] = None) -> float:
    """Calculates active engagement score (0.0 to 1.0) using last active date and GitHub.

    Applies linear decay on days since last logged active up to 180 days,
    and scales github activity score to [0.0, 1.0].

    Args:
        candidate (Dict): The candidate record dictionary.
        config (Optional[AppConfig]): Pipeline configuration object.

    Returns:
        float: Activity fit score.
    """
    if not isinstance(candidate, dict):
        return 0.0

    signals = candidate.get("redrob_signals", {})
    if not isinstance(signals, dict):
        return 0.0

    # 1. Parse active dates to compute inactivity decay
    last_active_str = signals.get("last_active_date")
    current_dt = get_reference_date(config)

    last_active_dt = parse_date(last_active_str) if last_active_str else None

    if last_active_dt:
        days = get_elapsed_days(last_active_dt, current_dt)
        # Linear decay mapping 0 days -> 1.0 down to 180 days -> 0.0
        active_score = max(0.0, 1.0 - (days / 180.0))
    else:
        active_score = 0.0

    # 2. Add GitHub contribution activity
    github_val = signals.get("github_activity_score", 0.0)
    try:
        github_val_float = float(github_val)
        if github_val_float < 0.0:
            github_score = 0.0
        else:
            github_score = min(1.0, github_val_float / 100.0)
    except (ValueError, TypeError):
        github_score = 0.0

    # Weighted blend: 70% active platform login, 30% github commits/PRs
    return float(0.7 * active_score + 0.3 * github_score)


def compute_notice_period_score(candidate: Dict) -> float:
    """Calculates notice period scoring (0.0 to 1.0) preferring immediate availability.

    Linear decay: 1.0 for immediate joiners (0 days notice) scaling down to 0.0 for 90 days.

    Args:
        candidate (Dict): The candidate record dictionary.

    Returns:
        float: Availability notice period score.
    """
    if not isinstance(candidate, dict):
        return 0.0

    signals = candidate.get("redrob_signals", {})
    if not isinstance(signals, dict):
        return 0.0

    np_days = signals.get("notice_period_days")
    if np_days is None:
        return 0.0

    try:
        days = max(0.0, float(np_days))
        return max(0.0, 1.0 - (days / 90.0))
    except (ValueError, TypeError):
        return 0.0


def compute_location_fit_score(candidate: Dict, jd_spec: Dict) -> float:
    """Calculates candidate location match scores using the feature engineering module.

    Reuses the robust location evaluation logic matching Noida/Pune primary hubs.

    Args:
        candidate (Dict): The candidate record dictionary.
        jd_spec (Dict): Structured job description specifications.

    Returns:
        float: Location alignment score.
    """
    return compute_location_score(candidate, jd_spec)


def compute_product_company_score(candidate: Dict) -> float:
    """Calculates a score indicating company history quality.

    - 0.0: Purely service-based consulting firms history.
    - 0.5: Mixed history of consulting and product firms.
    - 1.0: Strong product company career history.

    Args:
        candidate (Dict): The candidate record dictionary.

    Returns:
        float: Product company history score.
    """
    if not isinstance(candidate, dict):
        return 1.0

    career_history = candidate.get("career_history", [])
    if not isinstance(career_history, list) or not career_history:
        return 1.0

    consulting_companies = {
        "tcs",
        "infosys",
        "wipro",
        "accenture",
        "cognizant",
        "capgemini",
    }

    from src.honeypots import normalize_company_name

    job_count = 0
    consulting_job_count = 0

    for job in career_history:
        if not isinstance(job, dict):
            continue
        company = job.get("company")
        if company is None:
            continue

        job_count += 1
        normalized_name = normalize_company_name(company)

        # Token-based matches for service firms
        tokens = normalized_name.split()
        is_match = False
        for c in consulting_companies:
            if c in tokens or normalized_name.startswith(c):
                is_match = True
                break
        if is_match:
            consulting_job_count += 1

    if job_count == 0:
        return 1.0

    if consulting_job_count == job_count:
        return 0.0  # Consulting only
    elif consulting_job_count > 0:
        return 0.5  # Mixed history
    else:
        return 1.0  # Strong product history


def compute_behavioral_score(candidate: Dict, jd_spec: Dict, config: Optional[AppConfig] = None) -> float:
    """Combines all platform engagement and availability signals into a single score.

    Evaluates response rate, active decay, availability notice, and location alignment.
    Applies down-weight penalty if candidate is not open to work.

    Args:
        candidate (Dict): The candidate record dictionary.
        jd_spec (Dict): Structured job description specifications.
        config (Optional[AppConfig]): Pipeline configuration object.

    Returns:
        float: Combined behavioral score.
    """
    if not isinstance(candidate, dict):
        return 0.0

    # Compute constituent scores
    response_score = compute_response_rate_score(candidate)
    activity_score = compute_activity_score(candidate, config)
    notice_score = compute_notice_period_score(candidate)
    location_score = compute_location_fit_score(candidate, jd_spec)

    # Relocation and open availability checks
    signals = candidate.get("redrob_signals", {}) if isinstance(candidate, dict) else {}
    if not isinstance(signals, dict):
        signals = {}

    open_to_work = signals.get("open_to_work_flag", True)
    # Down-weight candidates not actively seeking roles
    open_multiplier = 1.0 if open_to_work else 0.8

    # Weighted blend: 30% response rate, 30% activity, 20% notice period, 20% location fit
    base_score = (
        0.30 * response_score +
        0.30 * activity_score +
        0.20 * notice_score +
        0.20 * location_score
    )

    return float(base_score * open_multiplier)


def fuse_scores(
    retrieval_score: float,
    semantic_score: float,
    behavioral_score: float,
    feature_vector: Dict[str, float],
    config: Optional[AppConfig] = None,
    candidate: Optional[Dict] = None,
) -> float:
    """Fuses all Stage 1 & 2 scores and behavioral metrics using configurable weights.

    Score contributions loaded dynamically from AppConfig configuration models:
    - semantic_match: 35%
    - experience_fit: 15%
    - product_company: 15%
    - behavioral_signals: 15%
    - preferred_skills: 10%
    - location: 10%

    Args:
        retrieval_score (float): Normalized BM25 stage 1 search score.
        semantic_score (float): Dense embedding similarity score.
        behavioral_score (float): Combined behavioral signal score.
        feature_vector (Dict[str, float]): Feature engineering scores mapping.
        config (Optional[AppConfig]): Pipeline configuration object.
        candidate (Optional[Dict]): The candidate record dictionary.

    Returns:
        float: Fused ranking score clamped in [0.0, 1.0].
    """
    # Load configuration if not provided
    if config is None:
        try:
            config = load_config()
        except Exception:
            pass

    # Default weights if config loading is bypassed
    w_semantic = 0.35
    w_experience = 0.15
    w_product = 0.15
    w_behavioral = 0.15
    w_preferred = 0.10
    w_location = 0.10

    if config and hasattr(config, "weights") and config.weights:
        try:
            w_semantic = config.weights.semantic_match / 100.0
            w_experience = config.weights.experience_fit / 100.0
            w_product = config.weights.product_company / 100.0
            w_behavioral = config.weights.behavioral_signals / 100.0
            w_preferred = config.weights.preferred_skills / 100.0
            w_location = config.weights.location / 100.0
        except Exception:
            pass

    # Retrieve values from feature engineering vector
    exp_score = feature_vector.get("experience_score", 0.0) if isinstance(feature_vector, dict) else 0.0
    pref_score = feature_vector.get("preferred_skill_score", 0.0) if isinstance(feature_vector, dict) else 0.0
    loc_score = feature_vector.get("location_score", 0.0) if isinstance(feature_vector, dict) else 0.0
    must_have_score = feature_vector.get("retrieval_skill_score", 0.0) if isinstance(feature_vector, dict) else 0.0

    # Calculate improved product company history score
    product_score = compute_product_company_score(candidate)

    # Correct Cosine Similarity normalization: mapping [-1.0, 1.0] -> [0.0, 1.0]
    normed_semantic = max(0.0, min(1.0, (float(semantic_score) + 1.0) / 2.0))

    # Blend Normalized Stage 1 BM25 and Stage 2 Semantic dense similarities
    semantic_match_blend = 0.5 * retrieval_score + 0.5 * normed_semantic

    # Fused rating scoring formula
    final_score = (
        w_semantic * semantic_match_blend +
        w_experience * exp_score +
        w_product * product_score +
        w_behavioral * behavioral_score +
        w_preferred * pref_score +
        w_location * loc_score
    )

    # Apply priority boost for candidates matching evaluation framework's Strong Fit skill criteria (>0.20)
    if must_have_score > 0.20:
        final_score += 0.25

    return float(final_score)


def rank_candidates(
    candidates: List[Dict],
    retrieval_metadata: Dict,
    semantic_metadata: Dict,
    jd_spec: Dict,
    config: Optional[AppConfig] = None,
) -> Tuple[List[Dict], Dict]:
    """Generates the final ranked candidates lists fusing stage 1 and 2 scoring vectors.

    Args:
        candidates (List[Dict]): List of candidates to rank.
        retrieval_metadata (Dict): Metadata scores from retrieval Stage 1.
        semantic_metadata (Dict): Metadata scores from dense reranker Stage 2.
        jd_spec (Dict): Structured job description specifications.
        config (Optional[AppConfig]): Pipeline configuration object.

    Returns:
        Tuple[List[Dict], Dict]: Ranked candidate list and scores metadata mapping.
    """
    if not candidates:
        logger.warning("Empty candidate list passed to rank_candidates. Returning empty ranked results.")
        return [], {"scores": {}}

    # Load config if not provided
    if config is None:
        try:
            config = load_config()
        except Exception as e:
            logger.warning("Could not load configuration inside rank_candidates: %s", str(e))

    # Compile a dictionary of candidate_id to their raw retrieval scores
    raw_ret_scores = {}
    for cand in candidates:
        if not isinstance(cand, dict):
            continue
        cand_id = cand.get("candidate_id")
        if cand_id is None:
            continue

        ret_score_meta = {}
        if isinstance(retrieval_metadata, dict):
            ret_scores = retrieval_metadata.get("scores", {})
            if cand_id in ret_scores:
                ret_score_meta = ret_scores[cand_id]
            elif str(cand_id) in ret_scores:
                ret_score_meta = ret_scores[str(cand_id)]

        raw_ret_scores[cand_id] = ret_score_meta.get("retrieval_score", 0.0) if isinstance(ret_score_meta, dict) else 0.0

    # Perform Min-Max scaling normalization over the raw retrieval scores
    if raw_ret_scores:
        min_ret = min(raw_ret_scores.values())
        max_ret = max(raw_ret_scores.values())
        ret_range = max_ret - min_ret
    else:
        min_ret = 0.0
        max_ret = 0.0
        ret_range = 0.0

    scored_candidates = []
    metadata_scores = {}

    for cand in candidates:
        if not isinstance(cand, dict):
            continue
        
        cand_id = cand.get("candidate_id")
        if cand_id is None:
            continue

        # Get normalized retrieval score
        raw_ret = raw_ret_scores.get(cand_id, 0.0)
        if ret_range > 1e-9:
            normed_ret = (raw_ret - min_ret) / ret_range
        else:
            normed_ret = 1.0 if raw_ret > 0.0 else 0.0

        # Retrieve Stage 2 score (defensive key checking supporting str and int)
        sem_score = 0.0
        if isinstance(semantic_metadata, dict):
            sem_scores = semantic_metadata.get("scores", {})
            if cand_id in sem_scores:
                sem_score = sem_scores[cand_id]
            elif str(cand_id) in sem_scores:
                sem_score = sem_scores[str(cand_id)]

        # Compute behavioral score
        beh_score = compute_behavioral_score(cand, jd_spec, config)

        # Generate component feature vector
        fv = build_feature_vector(cand, jd_spec)

        # Compute final fused score (passing normalized retrieval score)
        fused = fuse_scores(
            retrieval_score=normed_ret,
            semantic_score=sem_score,
            behavioral_score=beh_score,
            feature_vector=fv,
            config=config,
            candidate=cand,
        )

        scored_candidates.append((fused, cand))

        # Store breakdown scores in metadata mapping
        metadata_scores[cand_id] = {
            "raw_retrieval_score": float(raw_ret),
            "normalized_retrieval_score": float(normed_ret),
            "semantic_score": float(sem_score),
            "behavioral_score": float(beh_score),
            "feature_vector": fv,
            "fused_score": float(fused),
        }

    # Sort key: 1. Fused Score descending, 2. candidate_id ascending (tie-breaking)
    def sort_key(item):
        score, cand = item
        cand_id = cand.get("candidate_id", "")
        return (-score, str(cand_id))

    scored_candidates.sort(key=sort_key)

    # Compile ranked list and metadata structures
    ranked_candidates = []
    ranked_meta_list = []
    fused_scores = []

    for idx, (fused, cand) in enumerate(scored_candidates):
        rank = idx + 1
        cand_id = cand.get("candidate_id")

        # Copy candidate to safely inject rank metadata
        cand_copy = dict(cand)
        cand_copy["rank"] = rank
        cand_copy["fused_score"] = fused
        ranked_candidates.append(cand_copy)

        ranked_meta_list.append({
            "rank": rank,
            "candidate_id": cand_id,
            "fused_score": fused,
        })
        fused_scores.append(fused)

    processed_candidates = len(ranked_candidates)
    if processed_candidates > 0:
        average_score = sum(fused_scores) / processed_candidates
        max_score = max(fused_scores)
        min_score = min(fused_scores)
    else:
        average_score = 0.0
        max_score = 0.0
        min_score = 0.0

    metadata = {
        "statistics": {
            "processed_candidates": processed_candidates,
            "average_score": float(average_score),
            "max_score": float(max_score),
            "min_score": float(min_score),
        },
        "scores": metadata_scores,
        "ranked_list": ranked_meta_list,
    }

    logger.info("Successfully ranked and fused %d candidates.", processed_candidates)
    return ranked_candidates, metadata
