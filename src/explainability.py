from typing import Dict, List, Optional
from src.logger import PipelineLogger
from src.feature_engineering import extract_candidate_skills
from src.behavioral_scoring import compute_product_company_score, get_reference_date
from src.utils import parse_date, get_elapsed_days

logger = PipelineLogger.get_logger()


def extract_matched_skills(candidate: Dict, jd_spec: Dict) -> List[str]:
    """Intersects candidate skills with the job description specification.

    Args:
        candidate (Dict): The candidate record dictionary.
        jd_spec (Dict): Structured job description specifications.

    Returns:
        List[str]: List of matched skill names in Title Case.
    """
    if not isinstance(candidate, dict) or not isinstance(jd_spec, dict):
        return []

    candidate_skills = set(extract_candidate_skills(candidate))
    
    must_have = jd_spec.get("must_have", [])
    preferred = jd_spec.get("preferred", [])

    # Combine JD skills into a single set
    jd_skills = set()
    for skill in must_have + preferred:
        if isinstance(skill, str):
            jd_skills.add(skill.strip().lower())

    matched = candidate_skills.intersection(jd_skills)
    
    # Return matched skills ordered and title-cased for recruiter readability
    return sorted([skill.title() for skill in matched])


def generate_candidate_reasoning(
    candidate: Dict,
    score: float,
    rank: int,
    jd_spec: Dict,
) -> str:
    """Generates a factual, deterministic recruiter-facing reasoning string.

    Fuses experience years, matched skills, product/consulting history, and active signals.
    Strictly uses candidate facts. Maximum 2 sentences.

    Args:
        candidate (Dict): The candidate record dictionary.
        score (float): The final fused ranking score.
        rank (int): The rank of the candidate.
        jd_spec (Dict): Structured job description specifications.

    Returns:
        str: Factual 1-2 sentence explainability string.
    """
    if not isinstance(candidate, dict):
        return "Invalid candidate profile data provided."

    profile = candidate.get("profile", {})
    if not isinstance(profile, dict):
        profile = {}

    signals = candidate.get("redrob_signals", {})
    if not isinstance(signals, dict):
        signals = {}

    # 1. Gather Experience and Title
    curr_title = profile.get("current_title", "Engineer").strip()
    y_exp = profile.get("years_of_experience")
    try:
        y_exp_val = float(y_exp) if y_exp is not None else 0.0
    except (ValueError, TypeError):
        y_exp_val = 0.0

    # 2. Gather Matched Skills
    matched_skills = extract_matched_skills(candidate, jd_spec)
    skills_count = len(matched_skills)
    skills_str = ", ".join(matched_skills[:5])
    if len(matched_skills) > 5:
        skills_str += f", and {len(matched_skills) - 5} more"

    # 3. Resolve Product Company History
    prod_score = compute_product_company_score(candidate)
    if prod_score == 1.0:
        prod_desc = "strong product company history"
    elif prod_score == 0.5:
        prod_desc = "mixed product and consulting company history"
    else:
        prod_desc = "service-based consulting company history"

    # 4. Resolve Behavioral Availability and Activity
    response_val = signals.get("recruiter_response_rate", 0.0)
    try:
        response_rate = int(float(response_val) * 100)
    except (ValueError, TypeError):
        response_rate = 0

    np_val = signals.get("notice_period_days")
    try:
        np_days = int(float(np_val))
    except (ValueError, TypeError):
        np_days = 0

    # Inactivity decay check
    last_active_str = signals.get("last_active_date")
    ref_dt = get_reference_date()
    last_active_dt = parse_date(last_active_str) if last_active_str else None

    if last_active_dt:
        days = get_elapsed_days(last_active_dt, ref_dt)
        if days <= 30:
            active_desc = "active within 30 days"
        elif days <= 90:
            active_desc = "active within 90 days"
        else:
            active_desc = f"inactive for {days} days"
    else:
        active_desc = "no recent activity"

    # Sentence 1: Focuses on core fit, skills, and industry background
    sentence_1 = (
        f"{curr_title} with {y_exp_val:.1f} years of experience, "
        f"matching {skills_count} core skills ({skills_str or 'none'}) "
        f"and showing a {prod_desc}."
    )

    # Sentence 2: Focuses on availability and platform activity signals
    sentence_2 = (
        f"They are open to work ({active_desc}) with a {np_days}-day notice period "
        f"and {response_rate}% recruiter response rate."
    )

    return f"{sentence_1} {sentence_2}"


def generate_ranking_summary(ranked_candidates: List[Dict]) -> Dict:
    """Computes overall statistics and a readable text summary over the ranked candidate pool.

    Args:
        ranked_candidates (List[Dict]): List of candidates containing 'fused_score'.

    Returns:
        Dict: Overall summary statistics and textual summary string.
    """
    total = len(ranked_candidates)
    if total == 0:
        return {
            "total_candidates": 0,
            "score_statistics": {"min": 0.0, "max": 0.0, "average": 0.0},
            "experience_statistics": {"average_years": 0.0},
            "textual_summary": "No candidates were processed for ranking.",
        }

    fused_scores = []
    exp_years = []
    product_history_count = 0

    for cand in ranked_candidates:
        if not isinstance(cand, dict):
            continue
        
        # Fused score
        score = cand.get("fused_score", 0.0)
        fused_scores.append(score)

        # Experience
        profile = cand.get("profile", {})
        if isinstance(profile, dict):
            y_exp = profile.get("years_of_experience", 0.0)
            try:
                exp_years.append(float(y_exp))
            except (ValueError, TypeError):
                pass

        # Product check
        prod_score = compute_product_company_score(cand)
        if prod_score >= 0.5:
            product_history_count += 1

    # Score stats
    max_score = max(fused_scores) if fused_scores else 0.0
    min_score = min(fused_scores) if fused_scores else 0.0
    avg_score = sum(fused_scores) / len(fused_scores) if fused_scores else 0.0

    # Experience stats
    avg_exp = sum(exp_years) / len(exp_years) if exp_years else 0.0

    # Product ratio
    prod_ratio = (product_history_count / total) * 100 if total > 0 else 0.0

    text_summary = (
        f"Successfully ranked {total} candidates. "
        f"Fused scores range from {min_score:.4f} to {max_score:.4f} (average: {avg_score:.4f}). "
        f"The candidate pool has an average experience of {avg_exp:.1f} years, "
        f"with {prod_ratio:.1f}% showing product company background."
    )

    logger.info("Ranking explainability summary successfully compiled.")

    return {
        "total_candidates": total,
        "score_statistics": {
            "min": float(min_score),
            "max": float(max_score),
            "average": float(avg_score),
        },
        "experience_statistics": {
            "average_years": float(avg_exp),
        },
        "product_history_percentage": float(prod_ratio),
        "textual_summary": text_summary,
    }
