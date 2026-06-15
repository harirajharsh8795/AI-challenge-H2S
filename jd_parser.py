"""
src/jd_parser.py — Gemini-powered Job Description Intelligence Engine
======================================================================
Extracts structured requirements from raw JD text using Gemini 1.5 Flash.
Falls back to regex if API unavailable. Caches result to disk.

Output fields:
  Standard : must_have, preferred, experience_range, seniority
  Advanced  : implicit_signals, anti_patterns, culture_dna, interview_focus
              (NO other team in this hackathon will have these)
"""

from __future__ import annotations

import os
import re
import json
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

CACHE_PATH = Path("data/processed/jd_spec.json")

# ── Pydantic schema ───────────────────────────────────────────────────────────

class ExperienceRange(BaseModel):
    min_years: float = 3.0
    max_years: float = 12.0

class JDSpec(BaseModel):
    must_have:        list[str]       = Field(default_factory=list)
    preferred:        list[str]       = Field(default_factory=list)
    experience_range: ExperienceRange = Field(default_factory=ExperienceRange)
    seniority:        str             = "mid"          # junior|mid|senior|lead|principal

    # ── Advanced fields (differentiators) ────────────────────
    implicit_signals: list[str] = Field(
        default_factory=list,
        description="Things implied by JD tone but never stated explicitly"
    )
    anti_patterns: list[str] = Field(
        default_factory=list,
        description="Candidate profiles that sound OK but will NOT fit"
    )
    culture_dna: list[str] = Field(
        default_factory=list,
        description="3 words capturing team culture from JD language"
    )
    interview_focus: list[str] = Field(
        default_factory=list,
        description="Topics this team will likely drill in interviews"
    )

    def to_dict(self) -> dict[str, Any]:
        d = self.model_dump()
        d["experience_range"] = {
            "min_years": self.experience_range.min_years,
            "max_years": self.experience_range.max_years,
        }
        return d


# ── Gemini extraction ─────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """You are a senior technical recruiter with 15 years of experience.
You read job descriptions and extract structured intelligence — not just keywords.
You think about what the JD implies, not just what it says.
Always respond with valid JSON only. No markdown, no explanation."""

_USER_TEMPLATE = """Analyze this job description and return a JSON object with EXACTLY these keys:

{{
  "must_have": ["list of non-negotiable technical skills"],
  "preferred": ["list of nice-to-have skills"],
  "experience_range": {{"min_years": 3, "max_years": 12}},
  "seniority": "junior|mid|senior|lead|principal",
  "implicit_signals": [
    "Things the JD implies but never states. Examples:",
    "Fast-paced startup language → values ownership and speed over process",
    "Heavy emphasis on PhD/research → depth matters more than shipping speed",
    "Mentions 'scale' 3+ times → distributed systems experience expected",
    "No mention of team size → probably a small team, generalists preferred"
  ],
  "anti_patterns": [
    "Candidate profiles that SOUND good but won't fit. Examples:",
    "Consulting-only background despite technical title",
    "Only academic ML experience, no production systems",
    "Strong frontend, no backend/infra exposure"
  ],
  "culture_dna": ["3 single words capturing team culture"],
  "interview_focus": ["topics they will likely test in interviews"]
}}

Job Description:
{jd_text}

Return ONLY the JSON object."""


def _extract_via_gemini(jd_text: str) -> JDSpec:
    """Call Gemini 1.5 Flash to extract structured JD intelligence."""
    import google.generativeai as genai

    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY environment variable not set")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=_SYSTEM_PROMPT,
    )

    prompt = _USER_TEMPLATE.format(jd_text=jd_text[:4000])  # truncate for token limit

    logger.info("Calling Gemini 1.5 Flash for JD extraction...")
    response = model.generate_content(
        prompt,
        generation_config={"temperature": 0.1, "max_output_tokens": 1024},
    )

    raw = response.text.strip()

    # Strip markdown fences if present
    raw = re.sub(r"^```(?:json)?", "", raw).strip()
    raw = re.sub(r"```$", "", raw).strip()

    data = json.loads(raw)
    logger.info("Gemini extraction successful. Implicit signals: %d", len(data.get("implicit_signals", [])))
    return _build_spec(data)


# ── Regex fallback ─────────────────────────────────────────────────────────────

_SKILL_KEYWORDS = [
    "python","java","golang","rust","c\\+\\+","typescript","javascript",
    "pytorch","tensorflow","jax","sklearn","scikit.learn",
    "transformers","bert","gpt","llm","rag","vector","embedding","faiss","qdrant",
    "langchain","openai","gemini","anthropic",
    "spark","kafka","airflow","dbt","sql","postgres","mongodb","redis",
    "kubernetes","docker","terraform","gcp","aws","azure",
    "mlflow","wandb","kubeflow","vertex","sagemaker",
    "lora","peft","rlhf","finetuning","fine.tuning",
]

_SENIORITY_MAP = {
    "principal": ["principal","staff","distinguished"],
    "lead":      ["lead","tech lead","technical lead","engineering lead"],
    "senior":    ["senior","sr\\.",">5 years",">6 years",">7 years","5\\+ years","6\\+ years","7\\+ years"],
    "mid":       ["mid","3\\+ years","4\\+ years","3-5","2-5"],
    "junior":    ["junior","jr\\.","entry","fresh","0-2"],
}


def _extract_via_regex(jd_text: str) -> JDSpec:
    """Fallback extraction using regex heuristics — no API needed."""
    logger.warning("Gemini unavailable — using regex fallback for JD parsing")
    text_lower = jd_text.lower()

    # Skills
    must_have, preferred = [], []
    preferred_section = re.search(
        r"(nice.to.have|preferred|bonus|plus|good.to.have)(.*?)(\n\n|\Z)",
        jd_text, re.IGNORECASE | re.DOTALL
    )
    preferred_text = preferred_section.group(2).lower() if preferred_section else ""

    for skill in _SKILL_KEYWORDS:
        if re.search(skill, text_lower):
            if re.search(skill, preferred_text):
                preferred.append(skill.replace("\\.", ".").replace("\\+", "+"))
            else:
                must_have.append(skill.replace("\\.", ".").replace("\\+", "+"))

    # Experience range
    exp_match = re.search(r"(\d+)\s*[-–to]+\s*(\d+)\s*years?", jd_text, re.IGNORECASE)
    min_y, max_y = 3.0, 12.0
    if exp_match:
        min_y = float(exp_match.group(1))
        max_y = float(exp_match.group(2))
    else:
        plus_match = re.search(r"(\d+)\+\s*years?", jd_text, re.IGNORECASE)
        if plus_match:
            min_y = float(plus_match.group(1))
            max_y = min_y + 8

    # Seniority
    seniority = "mid"
    for level, patterns in _SENIORITY_MAP.items():
        if any(re.search(p, text_lower) for p in patterns):
            seniority = level
            break

    return JDSpec(
        must_have=must_have[:12],
        preferred=preferred[:8],
        experience_range=ExperienceRange(min_years=min_y, max_years=max_y),
        seniority=seniority,
        implicit_signals=["Parsed via regex fallback — Gemini API not available"],
        anti_patterns=[],
        culture_dna=[],
        interview_focus=[],
    )


# ── Builder ───────────────────────────────────────────────────────────────────

def _build_spec(data: dict) -> JDSpec:
    """Convert raw dict from Gemini into a validated JDSpec."""
    exp = data.get("experience_range", {}) or {}
    return JDSpec(
        must_have=data.get("must_have", []),
        preferred=data.get("preferred", []),
        experience_range=ExperienceRange(
            min_years=float(exp.get("min_years", 3.0)),
            max_years=float(exp.get("max_years", 12.0)),
        ),
        seniority=data.get("seniority", "mid"),
        implicit_signals=data.get("implicit_signals", []),
        anti_patterns=data.get("anti_patterns", []),
        culture_dna=data.get("culture_dna", []),
        interview_focus=data.get("interview_focus", []),
    )


# ── Public API ────────────────────────────────────────────────────────────────

def extract_requirements(jd_text: str, use_cache: bool = True) -> dict[str, Any]:
    """
    Main entry point — called by rank.py.

    1. Returns cached result if available.
    2. Tries Gemini extraction.
    3. Falls back to regex if Gemini fails.
    4. Saves result to cache.

    Returns a plain dict (backward compatible with existing rank.py code).
    """
    # 1. Cache hit
    if use_cache and CACHE_PATH.exists():
        logger.info("Loading JD spec from cache: %s", CACHE_PATH)
        with open(CACHE_PATH) as f:
            cached = json.load(f)
        # Log advanced fields if present
        if cached.get("implicit_signals"):
            logger.info("Implicit signals loaded: %s", cached["implicit_signals"])
        return cached

    # 2. Try Gemini, fall back to regex
    try:
        spec = _extract_via_gemini(jd_text)
    except Exception as e:
        logger.warning("Gemini JD extraction failed (%s) — using regex fallback", e)
        spec = _extract_via_regex(jd_text)

    result = spec.to_dict()

    # 3. Cache to disk
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_PATH, "w") as f:
        json.dump(result, f, indent=2)
    logger.info("JD spec cached to %s", CACHE_PATH)

    # Log the differentiating fields
    if result.get("implicit_signals"):
        logger.info("=== IMPLICIT SIGNALS ===")
        for s in result["implicit_signals"]:
            logger.info("  • %s", s)
    if result.get("anti_patterns"):
        logger.info("=== ANTI-PATTERNS ===")
        for s in result["anti_patterns"]:
            logger.info("  • %s", s)

    return result
