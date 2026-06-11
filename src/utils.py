import re
from datetime import date, datetime
from typing import Optional
from src.logger import PipelineLogger

logger = PipelineLogger.get_logger()


def parse_date(date_str: Optional[str]) -> Optional[date]:
    """Safely parses a ISO YYYY-MM-DD date string into a datetime.date object.

    Args:
        date_str (Optional[str]): The string representing the date.

    Returns:
        Optional[datetime.date]: The parsed date object, or None if parsing fails.
    """
    if not date_str or not isinstance(date_str, str):
        return None

    cleaned_str = date_str.strip()
    try:
        # Standard ISO YYYY-MM-DD format
        return datetime.strptime(cleaned_str, "%Y-%m-%d").date()
    except ValueError:
        try:
            # Fallback format checking: just year YYYY
            if re.match(r"^\d{4}$", cleaned_str):
                return date(int(cleaned_str), 1, 1)
        except ValueError as e:
            logger.warning("Failed to parse date year '%s': %s", cleaned_str, str(e))
        logger.warning("Invalid date format encountered: '%s'", cleaned_str)
        return None


def get_elapsed_days(start: Optional[date], end: Optional[date]) -> int:
    """Calculates the absolute difference in days between two date objects.

    Args:
        start (Optional[datetime.date]): The starting date.
        end (Optional[datetime.date]): The ending date.

    Returns:
        int: The absolute number of days between start and end. Returns 0 if either is None.
    """
    if not start or not end:
        return 0

    if not isinstance(start, date) or not isinstance(end, date):
        logger.error(
            "Invalid type passed to get_elapsed_days: start=%s, end=%s",
            type(start),
            type(end),
        )
        return 0

    return abs((end - start).days)


def sanitize_text(text: Optional[str]) -> str:
    """Cleans and standardizes free-text fields.

    Removes HTML markup tags, double spaces, and normalizes whitespaces.

    Args:
        text (Optional[str]): Unstructured text to sanitize.

    Returns:
        str: Sanitized, lowercase, trimmed string. Returns empty string if text is None.
    """
    if text is None:
        return ""

    if not isinstance(text, str):
        text = str(text)

    # 1. Strip HTML tags
    cleaned = re.sub(r"<[^>]+>", " ", text)
    # 2. Normalize whitespace, remove tabs, carriage returns, etc.
    cleaned = re.sub(r"\s+", " ", cleaned)
    # 3. Trim outer whitespaces and lowercase
    return cleaned.strip().lower()


def normalize_score(score: float, min_val: float, max_val: float) -> float:
    """Normalizes a score to a [0.0, 1.0] range using min-max scaling.

    If min_val and max_val are equal, returns 1.0 if score equals min_val, else 0.0.

    Args:
        score (float): The numeric score to normalize.
        min_val (float): The minimum bounding value.
        max_val (float): The maximum bounding value.

    Returns:
        float: The normalized score clamped between 0.0 and 1.0.
    """
    if not isinstance(score, (int, float)) or not isinstance(min_val, (int, float)) or not isinstance(max_val, (int, float)):
        logger.error("Non-numeric arguments passed to normalize_score.")
        return 0.0

    if min_val > max_val:
        logger.warning(
            "Min value (%s) is greater than Max value (%s). Swapping bounds.",
            min_val,
            max_val,
        )
        min_val, max_val = max_val, min_val

    if abs(max_val - min_val) < 1e-9:
        return 1.0 if abs(score - min_val) < 1e-9 else 0.0

    normalized = (score - min_val) / (max_val - min_val)
    # Clamp value within [0.0, 1.0] range to prevent rounding errors
    return max(0.0, min(1.0, normalized))


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely performs division, handling division by zero errors.

    Args:
        numerator (float): The dividend.
        denominator (float): The divisor.
        default (float): The value to return if denominator is 0.0.

    Returns:
        float: The quotient result of division, or the default value.
    """
    if not isinstance(numerator, (int, float)) or not isinstance(denominator, (int, float)):
        logger.error("Non-numeric arguments passed to safe_divide.")
        return default

    if abs(denominator) < 1e-9:
        return default

    return numerator / denominator
