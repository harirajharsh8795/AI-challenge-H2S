from datetime import date, datetime
from typing import Dict, Optional, Union
from src.logger import PipelineLogger
from src.utils import parse_date

logger = PipelineLogger.get_logger()


def normalize_company_name(name: Optional[str]) -> str:
    """Normalizes a company name for case-insensitive matching and space reduction.

    Args:
        name (Optional[str]): The raw company name.

    Returns:
        str: Normalized lowercase company name with extra spaces removed.
             Returns an empty string if name is None, empty, or not a string.
    """
    if name is None or not isinstance(name, str):
        return ""

    # Convert to lowercase, remove trailing spaces, replace consecutive whitespaces with a single space
    cleaned = name.strip().lower()
    return " ".join(cleaned.split())


def is_consulting_only(candidate: Dict) -> bool:
    """Checks if a candidate has only worked at consulting/service-based firms.

    Consulting firms list: TCS, Infosys, Wipro, Accenture, Cognizant, Capgemini.

    Args:
        candidate (Dict): The candidate profile data dictionary.

    Returns:
        bool: True if career history contains at least one job and all employers
              in career history belong to the consulting list, False otherwise.
    """
    if not isinstance(candidate, dict):
        return False

    career_history = candidate.get("career_history", [])
    if not isinstance(career_history, list) or not career_history:
        return False

    consulting_companies = {
        "tcs",
        "infosys",
        "wipro",
        "accenture",
        "cognizant",
        "capgemini",
    }

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
        
        # Check if any token matches the consulting list, or if the name starts with a target company name
        tokens = normalized_name.split()
        is_match = False
        for c in consulting_companies:
            if c in tokens or normalized_name.startswith(c):
                is_match = True
                break
                
        if is_match:
            consulting_job_count += 1

    # Check if there are valid jobs, and all of them match consulting companies
    if job_count > 0 and job_count == consulting_job_count:
        cand_id = candidate.get("candidate_id", "UNKNOWN")
        logger.debug(
            "[CONSULTING_ONLY_TRIGGERED] Candidate %s has consulting-only history.",
            cand_id,
        )
        return True

    return False


def is_honeypot(candidate: Dict, current_date: Union[str, date, datetime]) -> bool:
    """Determines whether a candidate profile contains logical anomalies (honeypots).

    Evaluates three rules:
    - Rule 1: Skill with 'expert'/'advanced' proficiency has exactly 0 duration.
    - Rule 2: Career entry duration exceeds elapsed calendar time by more than 24 months.
    - Rule 3: Declared experience is >= 1 year with empty history, or experience exceeds
              history duration by more than 3 years.

    Args:
        candidate (Dict): The candidate profile data dictionary.
        current_date (Union[str, date, datetime]): Pipeline reference date for duration math.

    Returns:
        bool: True if any honeypot logical anomaly is triggered, False otherwise.
    """
    if not isinstance(candidate, dict):
        return False

    # 1. Normalize current_date to date object
    ref_date: Optional[date] = None
    if isinstance(current_date, date):
        if isinstance(current_date, datetime):
            ref_date = current_date.date()
        else:
            ref_date = current_date
    elif isinstance(current_date, str):
        ref_date = parse_date(current_date)

    if ref_date is None:
        logger.error(
            "Invalid current_date '%s' passed to is_honeypot. Using date.today() as fallback.",
            current_date,
        )
        ref_date = date.today()

    cand_id = candidate.get("candidate_id", "UNKNOWN")

    # ==========================================
    # RULE 1: Expert/Advanced Skill with 0 Duration
    # ==========================================
    skills = candidate.get("skills", [])
    if isinstance(skills, list):
        for sk in skills:
            if not isinstance(sk, dict):
                continue
            prof = sk.get("proficiency")
            dur = sk.get("duration_months")

            if isinstance(prof, str) and prof.lower().strip() in ["expert", "advanced"]:
                if dur is not None and isinstance(dur, (int, float)) and dur == 0:
                    logger.debug(
                        "[RULE_1_TRIGGERED] Candidate %s flagged for skill '%s' with proficiency '%s' and 0 duration months.",
                        cand_id,
                        sk.get("name"),
                        prof,
                    )
                    return True

    # ==========================================
    # RULE 2: Stated Career Duration Mismatch
    # ==========================================
    career_history = candidate.get("career_history", [])
    if isinstance(career_history, list):
        for i, job in enumerate(career_history):
            if not isinstance(job, dict):
                continue

            stated_dur = job.get("duration_months")
            if stated_dur is None or not isinstance(stated_dur, (int, float)):
                continue

            start_str = job.get("start_date")
            end_str = job.get("end_date")
            is_current = job.get("is_current", False)

            start_dt = parse_date(start_str) if start_str else None
            if not start_dt:
                # Cannot compute calendar duration without start date, skip Rule 2 for this job
                continue

            if is_current or end_str is None:
                end_dt = ref_date
            else:
                end_dt = parse_date(end_str)

            if not end_dt:
                # Cannot compute calendar duration without valid end date, skip Rule 2 for this job
                continue

            elapsed_days = (end_dt - start_dt).days
            if elapsed_days < 0:
                elapsed_days = 0

            actual_months = elapsed_days / 30.4

            # If stated duration is longer than elapsed calendar duration by more than 24 months
            if stated_dur > actual_months + 24:
                logger.debug(
                    "[RULE_2_TRIGGERED] Candidate %s flagged at career entry %d: stated duration %s months, actual calendar months: %.2f.",
                    cand_id,
                    i + 1,
                    stated_dur,
                    actual_months,
                )
                return True

    # ==========================================
    # RULE 3: Declared Experience Mismatch
    # ==========================================
    profile = candidate.get("profile", {})
    if not isinstance(profile, dict):
        profile = {}

    y_exp = profile.get("years_of_experience")
    if y_exp is not None and isinstance(y_exp, (int, float)):
        # Condition 3a: years_of_experience >= 1 with empty history
        is_empty_history = True
        if isinstance(career_history, list) and len(career_history) > 0:
            valid_jobs = [job for job in career_history if isinstance(job, dict)]
            if valid_jobs:
                is_empty_history = False

        if y_exp >= 1.0 and is_empty_history:
            logger.debug(
                "[RULE_3_TRIGGERED] Candidate %s has years of experience %s but empty career history.",
                cand_id,
                y_exp,
            )
            return True

        # Condition 3b: years_of_experience - total_career_years > 3
        if isinstance(career_history, list) and not is_empty_history:
            total_duration_months = 0.0
            for job in career_history:
                if not isinstance(job, dict):
                    continue
                dur = job.get("duration_months", 0)
                if isinstance(dur, (int, float)):
                    total_duration_months += dur

            career_history_years = total_duration_months / 12.0
            if (y_exp - career_history_years) > 3.0:
                logger.debug(
                    "[RULE_3_TRIGGERED] Candidate %s flagged for experience gap: profile exp = %s, career history years = %.2f.",
                    cand_id,
                    y_exp,
                    career_history_years,
                )
                return True

    return False


def is_technical_role(candidate: Dict) -> bool:
    """Checks if the candidate has a technical engineering or data science role headline.

    Rejects headlines containing non-technical keywords (e.g. sales, marketing, operations)
    and requires technical engineering keywords (e.g. engineer, developer, scientist).
    """
    if not isinstance(candidate, dict):
        return False

    profile = candidate.get("profile", {})
    if not isinstance(profile, dict) or not profile:
        return False

    headline = profile.get("headline")
    if not headline or not isinstance(headline, str):
        return False

    headline_lower = headline.lower().strip()

    # 1. Reject lists (negative match)
    reject_keywords = [
        "sales", "marketing", "graphic", "operations", "mechanical", "civil",
        "recruiter", "hr ", "human resources", "talent acquisition", "accountant",
        "financial", "content writer", "copywriter", "customer support", "support specialist",
        "project manager", "operations manager", "social media", "legal", "compliance",
        "recruitment", "ui/ux designer", "product designer", "business development",
        "customer success", "sales executive", "business manager", "administrative",
        "helpdesk", "technician", "office manager"
    ]
    for word in reject_keywords:
        if word in headline_lower:
            return False

    # 2. Allow lists (positive match)
    allow_keywords = [
        "engineer", "developer", "scientist", "architect", "tech lead",
        "technical lead", "programmer", "ml", "ai", "nlp", "deep learning",
        "data analyst", "systems", "researcher", "coding", "software",
        "coder", "python", "tech", "technical"
    ]
    for word in allow_keywords:
        if word in headline_lower:
            return True

    return False
