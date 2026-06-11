import re
from typing import Dict, List, Optional
from src.logger import PipelineLogger

logger = PipelineLogger.get_logger()


def extract_candidate_skills(candidate: Dict) -> List[str]:
    """Extracts and normalizes the skills list from a candidate dictionary.

    Handles candidates with raw string skills list, dictionary-based skill formats,
    or missing skills values.

    Args:
        candidate (Dict): The candidate record dictionary.

    Returns:
        List[str]: A list of normalized, lowercase skill name strings.
    """
    if not isinstance(candidate, dict):
        return []

    skills_data = candidate.get("skills")
    if skills_data is None:
        return []

    normalized_skills = []

    # 1. Handle string format (e.g. "python, docker, faiss")
    if isinstance(skills_data, str):
        parts = re.split(r"[,;]+", skills_data)
        for part in parts:
            cleaned = part.strip().lower()
            if cleaned:
                normalized_skills.append(cleaned)
        return normalized_skills

    # 2. Handle dict format (e.g. {"python": "expert", "docker": "intermediate"})
    if isinstance(skills_data, dict):
        for k in skills_data.keys():
            if isinstance(k, str):
                cleaned = k.strip().lower()
                if cleaned:
                    normalized_skills.append(cleaned)
        return normalized_skills

    # 3. Handle list format (list of strings or list of dicts)
    if isinstance(skills_data, list):
        for skill in skills_data:
            if isinstance(skill, dict):
                # e.g., {"name": "Python", "proficiency": "expert"}
                name = skill.get("name")
                if isinstance(name, str):
                    cleaned = name.strip().lower()
                    if cleaned:
                        normalized_skills.append(cleaned)
            elif isinstance(skill, str):
                cleaned = skill.strip().lower()
                if cleaned:
                    normalized_skills.append(cleaned)

    return normalized_skills


def compute_retrieval_skill_score(candidate: Dict, jd_spec: Dict) -> float:
    """Calculates a normalized score (0.0 to 1.0) for the candidate's core retrieval skills.

    Intersects the candidate's skills with retrieval and evaluation clusters
    defined in the job description specification.

    Args:
        candidate (Dict): The candidate record dictionary.
        jd_spec (Dict): The parsed job description specification dictionary.

    Returns:
        float: Normalized retrieval skill matching score between 0.0 and 1.0.
    """
    if not isinstance(candidate, dict) or not isinstance(jd_spec, dict):
        return 0.0

    candidate_skills = set(extract_candidate_skills(candidate))

    # Core required retrieval/evaluation skills specified in the requirements
    core_retrieval_skills = {
        "embeddings",
        "retrieval",
        "vector search",
        "faiss",
        "pinecone",
        "qdrant",
        "weaviate",
        "bm25",
        "ndcg",
        "map",
        "mrr",
    }

    # Retrieve semantic clusters from JD specification
    clusters = jd_spec.get("semantic_clusters", {})
    if not isinstance(clusters, dict):
        clusters = {}

    retrieval_skills = clusters.get("retrieval", [])
    eval_skills = clusters.get("evaluation", [])

    # Combine core list with any parsed retrieval/evaluation skills
    target_skills = set(core_retrieval_skills)
    for skill in retrieval_skills + eval_skills:
        if isinstance(skill, str):
            target_skills.add(skill.strip().lower())

    if not target_skills:
        return 0.0

    overlap = candidate_skills.intersection(target_skills)
    total_targets = len(target_skills)

    score = len(overlap) / total_targets
    
    cand_id = candidate.get("candidate_id", "UNKNOWN")
    logger.debug(
        "Candidate %s core retrieval score: %.4f (%d/%d matches)",
        cand_id,
        score,
        len(overlap),
        total_targets,
    )
    return float(score)


def compute_experience_score(candidate: Dict, jd_spec: Dict) -> float:
    """Calculates a normalized score (0.0 to 1.0) indicating experience fit.

    Scores 1.0 if years_of_experience falls inside the JD target range.
    Applies linear decay penalty if experience falls below the minimum,
    and a small fractional penalty for years exceeding the maximum.

    Args:
        candidate (Dict): The candidate record dictionary.
        jd_spec (Dict): The parsed job description specification dictionary.

    Returns:
        float: Normalized experience score between 0.0 and 1.0.
    """
    if not isinstance(candidate, dict) or not isinstance(jd_spec, dict):
        return 0.0

    profile = candidate.get("profile", {})
    if not isinstance(profile, dict):
        profile = {}

    y_exp = profile.get("years_of_experience")
    if y_exp is None:
        return 0.0

    try:
        y_exp_val = max(0.0, float(y_exp))
    except (ValueError, TypeError):
        return 0.0

    exp_range = jd_spec.get("experience_range", {})
    if not isinstance(exp_range, dict):
        exp_range = {}

    min_y = exp_range.get("min_years")
    max_y = exp_range.get("max_years")

    # Safe defaults representing the main JD profile target
    if min_y is None:
        min_y = 5.0
    if max_y is None:
        max_y = 9.0

    try:
        min_y_val = max(0.0, float(min_y))
        max_y_val = max(0.0, float(max_y))
    except (ValueError, TypeError):
        min_y_val = 5.0
        max_y_val = 9.0

    # Ensure min <= max
    if min_y_val > max_y_val:
        min_y_val, max_y_val = max_y_val, min_y_val

    # Calculate score
    if y_exp_val < min_y_val:
        # Linear penalty for experience below target min
        score = y_exp_val / min_y_val if min_y_val > 0.0 else 0.0
    elif y_exp_val > max_y_val:
        # Apply fractional penalty (decay of 0.05 per year exceeding max)
        gap = y_exp_val - max_y_val
        score = max(0.0, 1.0 - (gap * 0.05))
    else:
        score = 1.0

    return float(score)


def compute_location_score(candidate: Dict, jd_spec: Dict) -> float:
    """Calculates a normalized score (0.0 to 1.0) representing location alignment.

    Scores 1.0 for Noida/Pune, 0.8 for other Indian target tech hubs,
    and decays to 0.4–0.6 for candidates willing to relocate.

    Args:
        candidate (Dict): The candidate record dictionary.
        jd_spec (Dict): The parsed job description specification dictionary.

    Returns:
        float: Normalized location alignment score between 0.0 and 1.0.
    """
    if not isinstance(candidate, dict) or not isinstance(jd_spec, dict):
        return 0.0

    profile = candidate.get("profile", {})
    if not isinstance(profile, dict):
        profile = {}

    cand_loc = profile.get("location")
    cand_country = profile.get("country")

    cand_loc_lower = str(cand_loc).lower().strip() if cand_loc is not None else ""
    cand_country_lower = str(cand_country).lower().strip() if cand_country is not None else ""

    # Normalize location preferences from JD spec
    target_locations = []
    if isinstance(jd_spec, dict):
        locs = jd_spec.get("locations")
        if isinstance(locs, list):
            target_locations = [str(loc).lower().strip() for loc in locs if loc]

    if not target_locations:
        target_locations = ["noida", "pune", "hyderabad", "mumbai", "delhi ncr", "bangalore", "chennai"]

    primary_targets = {"noida", "pune", "delhi", "delhi ncr"}
    secondary_targets = {"hyderabad", "mumbai", "bangalore", "bengaluru", "chennai"}

    # 1. Search for explicit match in candidate's city description
    # Check primary targets first
    for target in primary_targets:
        if target in cand_loc_lower:
            return 1.0

    # Check secondary targets
    for target in secondary_targets:
        if target in cand_loc_lower:
            return 0.8

    # General check for parsed JD targets
    for target in target_locations:
        if target in cand_loc_lower:
            if target in primary_targets:
                return 1.0
            return 0.8

    # 2. Relocation and general region match checks
    signals = candidate.get("redrob_signals", {}) if isinstance(candidate, dict) else {}
    if not isinstance(signals, dict):
        signals = {}
    willing_relocate = signals.get("willing_to_relocate", False)

    if willing_relocate:
        if "india" in cand_country_lower or "india" in cand_loc_lower:
            return 0.6
        return 0.4

    # 3. Candidate is in India but not in target cities and unwilling to relocate
    if "india" in cand_country_lower or "india" in cand_loc_lower:
        return 0.3

    return 0.0


def compute_preferred_skill_score(candidate: Dict, jd_spec: Dict) -> float:
    """Calculates a normalized score (0.0 to 1.0) matching secondary/preferred skills.

    Evaluates LLM (LoRA, PEFT) and systems operations skills (Python, Docker, Kubernetes).

    Args:
        candidate (Dict): The candidate record dictionary.
        jd_spec (Dict): The parsed job description specification dictionary.

    Returns:
        float: Normalized preferred skill match score between 0.0 and 1.0.
    """
    if not isinstance(candidate, dict) or not isinstance(jd_spec, dict):
        return 0.0

    candidate_skills = set(extract_candidate_skills(candidate))

    # Core preferred skills
    core_preferred_skills = {
        "lora",
        "qlora",
        "peft",
        "fine tuning",
        "python",
        "docker",
        "kubernetes",
    }

    # Incorporate preferred list and semantic clusters
    preferred_list = jd_spec.get("preferred", []) if isinstance(jd_spec, dict) else []
    if not isinstance(preferred_list, list):
        preferred_list = []

    clusters = jd_spec.get("semantic_clusters", {})
    if not isinstance(clusters, dict):
        clusters = {}

    llm_skills = clusters.get("llm", [])
    systems_skills = clusters.get("systems", [])

    # Compile the combined set of preferred skills
    all_preferred = set(core_preferred_skills)
    for skill in preferred_list + llm_skills + systems_skills:
        if isinstance(skill, str):
            all_preferred.add(skill.strip().lower())

    if not all_preferred:
        return 0.0

    overlap = candidate_skills.intersection(all_preferred)
    total_targets = len(all_preferred)

    score = len(overlap) / total_targets
    return float(score)


def build_feature_vector(candidate: Dict, jd_spec: Dict) -> Dict[str, float]:
    """Generates the unified dictionary containing all normalized feature scores.

    Handles edge cases defensively to ensure all scores are float values.

    Args:
        candidate (Dict): The candidate record dictionary.
        jd_spec (Dict): The parsed job description specification dictionary.

    Returns:
        Dict[str, float]: Features mapping score names to float values.
    """
    return {
        "retrieval_skill_score": compute_retrieval_skill_score(candidate, jd_spec),
        "experience_score": compute_experience_score(candidate, jd_spec),
        "location_score": compute_location_score(candidate, jd_spec),
        "preferred_skill_score": compute_preferred_skill_score(candidate, jd_spec),
    }
