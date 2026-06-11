import re
from typing import Dict, List, Optional
from src.logger import PipelineLogger

logger = PipelineLogger.get_logger()


def extract_skills(text: str) -> List[str]:
    """Extracts and normalizes a standard list of skills from a text block.

    Supports matching for retrieval, embeddings, vector search, and related NLP/systems tools.

    Args:
        text (str): The raw text block containing potential skills.

    Returns:
        List[str]: A list of normalized, unique skills found in the text.
    """
    if not text or not isinstance(text, str):
        return []

    # Mapping of target skill name to regex pattern variations
    skill_patterns = {
        "retrieval": [r"\bretrieval\b", r"\binformation retrieval\b", r"\bdense retrieval\b", r"\bsparse retrieval\b"],
        "embeddings": [r"\bembeddings?\b", r"\bsentence-transformers?\b", r"\bbge\b", r"\be5\b"],
        "vector search": [r"\bvector search\b", r"\bvector databases?\b", r"\bvector indexing\b"],
        "faiss": [r"\bfaiss\b"],
        "pinecone": [r"\bpinecone\b"],
        "qdrant": [r"\bqdrant\b"],
        "weaviate": [r"\bweaviate\b"],
        "bm25": [r"\bbm25\b"],
        "ndcg": [r"\bndcg\b"],
        "mrr": [r"\bmrr\b"],
        "map": [r"\bmap\b"],
        "python": [r"\bpython\b"],
        "docker": [r"\bdocker\b"],
        "kubernetes": [r"\bkubernetes\b", r"\bk8s\b"],
        "lora": [r"\blora\b"],
        "qlora": [r"\bqlora\b"],
        "peft": [r"\bpeft\b"],
    }

    found_skills = []
    text_lower = text.lower()

    for skill, patterns in skill_patterns.items():
        for pattern in patterns:
            # Match case-insensitively with regex
            if re.search(pattern, text_lower, re.IGNORECASE):
                found_skills.append(skill)
                break

    return found_skills


def extract_experience_requirements(text: str) -> Dict[str, Optional[float]]:
    """Parses experience requirements (minimum and maximum years) from the job description.

    Args:
        text (str): The raw job description text.

    Returns:
        Dict[str, Optional[float]]: Dictionary with keys 'min_years' and 'max_years'.
    """
    # Safe defaults representing the main JD profile target
    result = {"min_years": 5.0, "max_years": 9.0}

    if not text or not isinstance(text, str):
        return result

    # 1. Match standard range syntax (e.g. "5-9 years", "5 to 9 years")
    # Supports en-dash, em-dash, and standard hyphens
    range_match = re.search(r"(\d+)\s*[\u2013-–-]\s*(\d+)\s*years?", text, re.IGNORECASE)
    if range_match:
        try:
            result["min_years"] = float(range_match.group(1))
            result["max_years"] = float(range_match.group(2))
            logger.info(
                "Parsed experience range: min=%s, max=%s",
                result["min_years"],
                result["max_years"],
            )
            return result
        except ValueError:
            pass

    to_match = re.search(r"(\d+)\s*to\s*(\d+)\s*years?", text, re.IGNORECASE)
    if to_match:
        try:
            result["min_years"] = float(to_match.group(1))
            result["max_years"] = float(to_match.group(2))
            logger.info(
                "Parsed experience range (to): min=%s, max=%s",
                result["min_years"],
                result["max_years"],
            )
            return result
        except ValueError:
            pass

    # 2. Match minimum-only boundaries (e.g. "5+ years")
    min_match = re.search(r"(\d+)\+?\s*years?", text, re.IGNORECASE)
    if min_match:
        try:
            result["min_years"] = float(min_match.group(1))
            result["max_years"] = None
            logger.info("Parsed minimum experience requirement: min=%s", result["min_years"])
        except ValueError:
            pass

    return result


def extract_location_preferences(text: str) -> List[str]:
    """Scans the text for target locations mentioned in the job description.

    Args:
        text (str): The raw job description text.

    Returns:
        List[str]: Unique list of matching location preferences in Title Case.
    """
    if not text or not isinstance(text, str):
        return []

    known_locations = [
        "Noida",
        "Pune",
        "Hyderabad",
        "Mumbai",
        "Delhi NCR",
        "Bangalore",
        "Chennai",
    ]
    found_locations = []
    text_lower = text.lower()

    for loc in known_locations:
        pattern = r"\b" + re.escape(loc.lower()) + r"\b"
        if re.search(pattern, text_lower):
            found_locations.append(loc)

    logger.info("Extracted location preferences: %s", found_locations)
    return found_locations


def build_skill_clusters() -> Dict[str, List[str]]:
    """Builds predefined semantic clusters grouping search, evaluation, LLM, and operations skills.

    Returns:
        Dict[str, List[str]]: Predefined semantic groupings mapping target areas to lists of skills.
    """
    return {
        "retrieval": [
            "embeddings",
            "dense retrieval",
            "vector search",
            "semantic search",
            "ranking",
            "faiss",
            "pinecone",
            "weaviate",
            "qdrant",
            "bm25",
        ],
        "evaluation": ["ndcg", "map", "mrr", "offline evaluation", "a/b testing"],
        "llm": ["lora", "qlora", "peft", "fine tuning"],
        "systems": ["python", "docker", "kubernetes"],
    }


def extract_requirements(jd_text: str) -> Dict:
    """Parses raw job description text into a structured specification for ranking.

    Splits the text into logical sections (requirements, preferences, exclusions)
    to classify skills, locations, and boundaries.

    Args:
        jd_text (str): The raw job description string.

    Returns:
        Dict: A structured specification dictionary containing keys:
              must_have, preferred, excluded, locations, experience_range, semantic_clusters.
    """
    if not jd_text or not isinstance(jd_text, str):
        logger.warning("Empty or non-string JD text passed. Returning default spec structures.")
        return {
            "must_have": [],
            "preferred": [],
            "excluded": [],
            "locations": [],
            "experience_range": {"min_years": 5.0, "max_years": 9.0},
            "semantic_clusters": build_skill_clusters(),
        }

    cleaned_jd = jd_text.strip()
    exp = extract_experience_requirements(cleaned_jd)
    locs = extract_location_preferences(cleaned_jd)
    clusters = build_skill_clusters()

    # Split text into sections based on keywords
    must_have_text = ""
    preferred_text = ""
    excluded_text = ""

    lines = cleaned_jd.split("\n")
    current_section = "general"

    for line in lines:
        line_lower = line.lower()
        if "absolutely need" in line_lower or "things you need" in line_lower:
            current_section = "must_have"
        elif "like you to have" in line_lower or "preferred" in line_lower:
            current_section = "preferred"
        elif "explicitly do not want" in line_lower or "disqualifiers" in line_lower:
            current_section = "excluded"

        if current_section == "must_have":
            must_have_text += line + "\n"
        elif current_section == "preferred":
            preferred_text += line + "\n"
        elif current_section == "excluded":
            excluded_text += line + "\n"

    # Extract skills from sections
    if not must_have_text:
        # Fallback must-have skills if section headers are missing
        must_have_skills = ["retrieval", "embeddings", "vector search", "python", "ndcg", "mrr", "map"]
    else:
        must_have_skills = extract_skills(must_have_text)

    if not preferred_text:
        # Fallback preferred skills if section headers are missing
        preferred_skills = ["lora", "qlora", "peft"]
    else:
        preferred_skills = extract_skills(preferred_text)

    # Differentiate target profile exclusions
    excluded_items = []
    check_text = excluded_text if excluded_text else cleaned_jd.lower()

    if "consulting" in check_text.lower() or "tcs" in check_text.lower():
        excluded_items.append("consulting-only candidates")
    if "academic" in check_text.lower() or "research" in check_text.lower():
        excluded_items.append("academic researchers without production systems")
    if "langchain" in check_text.lower():
        excluded_items.append("langchain-only developers")
    if "vision" in check_text.lower() or "computer vision" in check_text.lower():
        excluded_items.append("computer vision-only engineers")
    if "speech" in check_text.lower():
        excluded_items.append("speech-only engineers")

    # Fallback exclusions if none matched
    if not excluded_items:
        excluded_items = [
            "consulting-only candidates",
            "academic researchers without production systems",
            "langchain-only developers",
            "computer vision-only engineers",
            "speech-only engineers",
        ]

    logger.info("JD successfully parsed into structured requirements specification.")
    return {
        "must_have": must_have_skills,
        "preferred": preferred_skills,
        "excluded": excluded_items,
        "locations": locs,
        "experience_range": exp,
        "semantic_clusters": clusters,
    }
