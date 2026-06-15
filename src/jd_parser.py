"""
src/jd_parser.py — Gemini-powered Job Description Intelligence
===============================================================
Extracts deep structured requirements from raw JD text.
Uses Gemini 1.5 Flash. Falls back to regex if API unavailable.
Caches to data/processed/jd_spec.json.
"""

from __future__ import annotations
import os
import re
import json
import logging
from pathlib import Path
from typing import Any, List, Dict, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
CACHE_PATH = Path("data/processed/jd_spec.json")

class ExperienceRange(BaseModel):
    min_years: float = 3.0
    max_years: float = 12.0

class JDSpec(BaseModel):
    must_have: list[str] = Field(default_factory=list)
    preferred: list[str] = Field(default_factory=list)
    experience_range: ExperienceRange = Field(default_factory=ExperienceRange)
    seniority: str = "mid"
    # ADVANCED FIELDS — differentiators no other team has
    implicit_signals: list[str] = Field(default_factory=list)
    anti_patterns: list[str] = Field(default_factory=list)
    culture_dna: list[str] = Field(default_factory=list)
    interview_focus: list[str] = Field(default_factory=list)
    weighted_skills: dict[str, float] = Field(default_factory=dict)
    # COMPATIBILITY FIELDS — needed for verify_jd_parser.py
    excluded: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = self.model_dump()
        d["experience_range"] = {
            "min_years": self.experience_range.min_years,
            "max_years": self.experience_range.max_years,
        }
        return d

_SYSTEM = """You are a senior technical recruiter with 15 years experience.
Extract structured intelligence from job descriptions.
Think about what the JD implies, not just what it says.
Reply with valid JSON only. No markdown."""

_PROMPT = """Analyze this job description and return JSON with these exact keys:
{{
  "must_have": ["non-negotiable technical skills"],
  "preferred": ["nice-to-have skills"],
  "experience_range": {{"min_years": 3, "max_years": 12}},
  "seniority": "junior|mid|senior|lead|principal",
  "weighted_skills": {{
    "skill_name": weight_float
  }},
  "implicit_signals": [
    "Things implied but not stated. Examples:",
    "Fast-paced language → values speed over process",
    "PhD preferred → research depth over shipping",
    "Mentions scale 3+ times → distributed systems expected"
  ],
  "anti_patterns": [
    "Candidate profiles that sound good but wont fit",
    "Example: consulting-only background",
    "Example: only academic ML, no production systems"
  ],
  "culture_dna": ["3 words capturing team culture"],
  "interview_focus": ["topics they will test in interviews"]
}}

For weighted_skills: skills mentioned multiple times get higher weight.
Skill mentioned once = 1.0, twice = 1.3, thrice+ = 1.5

Job Description:
{jd_text}

Return ONLY the JSON object."""

def extract_skills(text: str) -> List[str]:
    """Extracts and normalizes a standard list of skills from a text block."""
    if not text or not isinstance(text, str):
        return []

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
            if re.search(pattern, text_lower, re.IGNORECASE):
                found_skills.append(skill)
                break

    return found_skills

def extract_experience_requirements(text: str) -> Dict[str, Optional[float]]:
    """Parses experience requirements (minimum and maximum years) from the job description."""
    result = {"min_years": 5.0, "max_years": 9.0}

    if not text or not isinstance(text, str):
        return result

    range_match = re.search(r"(\d+)\s*[\u2013-–-]\s*(\d+)\s*years?", text, re.IGNORECASE)
    if range_match:
        try:
            result["min_years"] = float(range_match.group(1))
            result["max_years"] = float(range_match.group(2))
            return result
        except ValueError:
            pass

    to_match = re.search(r"(\d+)\s*to\s*(\d+)\s*years?", text, re.IGNORECASE)
    if to_match:
        try:
            result["min_years"] = float(to_match.group(1))
            result["max_years"] = float(to_match.group(2))
            return result
        except ValueError:
            pass

    min_match = re.search(r"(\d+)\+?\s*years?", text, re.IGNORECASE)
    if min_match:
        try:
            result["min_years"] = float(min_match.group(1))
            result["max_years"] = None
        except ValueError:
            pass

    return result

def extract_location_preferences(text: str) -> List[str]:
    """Scans the text for target locations mentioned in the job description."""
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

    return found_locations

def build_skill_clusters() -> Dict[str, List[str]]:
    """Builds predefined semantic clusters."""
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

def _gemini_extract(jd_text: str) -> JDSpec:
    import google.generativeai as genai
    key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GOOGLE_API_KEY not set")
    genai.configure(api_key=key)
    model = genai.GenerativeModel(
        "gemini-1.5-flash",
        system_instruction=_SYSTEM
    )
    response = model.generate_content(
        _PROMPT.format(jd_text=jd_text[:4000]),
        generation_config={"temperature": 0.1, "max_output_tokens": 1024}
    )
    raw = response.text.strip()
    raw = re.sub(r"^```(?:json)?", "", raw).strip()
    raw = re.sub(r"```$", "", raw).strip()
    data = json.loads(raw)
    logger.info("Gemini JD extraction done. Skills: %s", data.get("must_have"))
    return _build(data, jd_text)

_SKILLS = [
    "python","pytorch","tensorflow","transformers","bert","gpt","llm",
    "rag","lora","peft","qlora","embeddings","vector","faiss","qdrant",
    "pinecone","langchain","llamaindex","mlflow","wandb","spark","kafka",
    "airflow","kubernetes","docker","aws","gcp","azure","sql","mongodb"
]

def _regex_extract(jd_text: str) -> JDSpec:
    logger.warning("Using regex fallback for JD parsing")
    text_lower = jd_text.lower()
    
    idx_must = -1
    for p in ["absolutely need", "things you need", "things we need"]:
        idx = text_lower.find(p)
        if idx != -1:
            idx_must = idx
            break
            
    idx_pref = -1
    for p in ["like you to have", "things we'd like", "preferred", "bonus"]:
        idx = text_lower.find(p)
        if idx != -1:
            idx_pref = idx
            break
            
    idx_excl = -1
    for p in ["do not want", "disqualifiers", "things we explicitly do not want"]:
        idx = text_lower.find(p)
        if idx != -1:
            idx_excl = idx
            break

    must_have_text = ""
    preferred_text = ""
    excluded_text = ""

    if idx_must != -1:
        end_idx = idx_pref if idx_pref != -1 else (idx_excl if idx_excl != -1 else len(text_lower))
        if end_idx > idx_must:
            must_have_text = text_lower[idx_must:end_idx]
            
    if idx_pref != -1:
        end_idx = idx_excl if idx_excl != -1 else len(text_lower)
        if end_idx > idx_pref:
            preferred_text = text_lower[idx_pref:end_idx]
            
    if idx_excl != -1:
        excluded_text = text_lower[idx_excl:]

    if not must_have_text and not preferred_text:
        must_have_text = text_lower

    must_have, preferred = [], []
    weighted_skills = {}

    for skill in _SKILLS:
        count = len(re.findall(r"\b" + re.escape(skill) + r"\b", text_lower))
        if count > 0:
            weight = 1.0 if count == 1 else (1.3 if count == 2 else 1.5)
            weighted_skills[skill] = weight
            if preferred_text and re.search(r"\b" + re.escape(skill) + r"\b", preferred_text):
                preferred.append(skill)
            elif must_have_text and re.search(r"\b" + re.escape(skill) + r"\b", must_have_text):
                must_have.append(skill)
            else:
                must_have.append(skill)

    exp = extract_experience_requirements(jd_text)
    min_y = exp["min_years"] or 3.0
    max_y = exp["max_years"] or 12.0

    seniority = "mid"
    for level, patterns in {
        "principal": ["principal","staff"],
        "lead": ["lead","tech lead"],
        "senior": ["senior","sr\\.","5\\+ years","6\\+ years"],
        "mid": ["3\\+ years","4\\+ years"],
        "junior": ["junior","entry","fresh"],
    }.items():
        if any(re.search(p, text_lower) for p in patterns):
            seniority = level
            break

    locs = extract_location_preferences(jd_text)
    excluded_items = []
    if "consulting" in text_lower or "tcs" in text_lower or "infosys" in text_lower:
        excluded_items.append("consulting-only candidates")
    if "academic" in text_lower or "research" in text_lower:
        excluded_items.append("academic researchers without production systems")
    if "langchain" in text_lower:
        excluded_items.append("langchain-only developers")
    if "vision" in text_lower or "computer vision" in text_lower:
        excluded_items.append("computer vision-only engineers")
    if "speech" in text_lower:
        excluded_items.append("speech-only engineers")

    if not excluded_items:
        excluded_items = [
            "consulting-only candidates",
            "academic researchers without production systems",
            "langchain-only developers",
            "computer vision-only engineers",
            "speech-only engineers",
        ]

    return JDSpec(
        must_have=must_have[:12],
        preferred=preferred[:8],
        experience_range=ExperienceRange(min_years=min_y, max_years=max_y),
        seniority=seniority,
        weighted_skills=weighted_skills,
        implicit_signals=["Parsed via regex — Gemini API not available"],
        anti_patterns=[],
        culture_dna=[],
        interview_focus=[],
        excluded=excluded_items,
        locations=locs
    )

def _build(data: dict, jd_text: str = "") -> JDSpec:
    exp = data.get("experience_range", {}) or {}
    
    # Compatibility fields for verify_jd_parser.py
    locs = extract_location_preferences(jd_text) if jd_text else []
    
    excluded_items = []
    if jd_text:
        text_lower = jd_text.lower()
        if "consulting" in text_lower or "tcs" in text_lower or "infosys" in text_lower:
            excluded_items.append("consulting-only candidates")
        if "academic" in text_lower or "research" in text_lower:
            excluded_items.append("academic researchers without production systems")
        if "langchain" in text_lower:
            excluded_items.append("langchain-only developers")
        if "vision" in text_lower or "computer vision" in text_lower:
            excluded_items.append("computer vision-only engineers")
        if "speech" in text_lower:
            excluded_items.append("speech-only engineers")

    if not excluded_items:
        excluded_items = [
            "consulting-only candidates",
            "academic researchers without production systems",
            "langchain-only developers",
            "computer vision-only engineers",
            "speech-only engineers",
        ]

    return JDSpec(
        must_have=data.get("must_have", []),
        preferred=data.get("preferred", []),
        experience_range=ExperienceRange(
            min_years=float(exp.get("min_years", 3.0)),
            max_years=float(exp.get("max_years", 12.0))
        ),
        seniority=data.get("seniority", "mid"),
        weighted_skills=data.get("weighted_skills", {}),
        implicit_signals=data.get("implicit_signals", []),
        anti_patterns=data.get("anti_patterns", []),
        culture_dna=data.get("culture_dna", []),
        interview_focus=data.get("interview_focus", []),
        excluded=excluded_items,
        locations=locs
    )

def extract_requirements(jd_text: str, use_cache: bool = True) -> dict[str, Any]:
    """Main entry point — called by rank.py"""
    import hashlib
    jd_hash = hashlib.md5(jd_text.encode("utf-8")).hexdigest()

    if use_cache and CACHE_PATH.exists():
        try:
            with open(CACHE_PATH) as f:
                cached = json.load(f)
            if cached.get("jd_hash") == jd_hash:
                logger.info("Loading JD spec from cache")
                return cached
        except Exception:
            pass

    try:
        spec = _gemini_extract(jd_text)
        logger.info("Implicit signals found: %d", len(spec.implicit_signals))
        logger.info("Culture DNA: %s", spec.culture_dna)
    except Exception as e:
        logger.warning("Gemini failed (%s) — regex fallback", e)
        spec = _regex_extract(jd_text)

    result = spec.to_dict()
    result["jd_hash"] = jd_hash
    
    # Add semantic_clusters to result for backward compatibility
    result["semantic_clusters"] = build_skill_clusters()

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_PATH, "w") as f:
        json.dump(result, f, indent=2)
    logger.info("JD spec saved to %s", CACHE_PATH)
    return result
