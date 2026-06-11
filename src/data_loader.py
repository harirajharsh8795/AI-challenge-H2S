import gzip
import json
import os
from typing import Dict, Generator
from src.logger import PipelineLogger
from src.utils import sanitize_text

logger = PipelineLogger.get_logger()


def validate_candidate_schema(candidate: Dict) -> bool:
    """Performs a lightweight schema validation check on a candidate record.

    Ensures the presence of all required fields defined in candidate_schema.json
    and validates their core structural data types.

    Args:
        candidate (Dict): The parsed candidate record dictionary.

    Returns:
        bool: True if the record meets schema expectations, False otherwise.
    """
    if not isinstance(candidate, dict):
        return False

    required_fields = [
        "candidate_id",
        "profile",
        "career_history",
        "education",
        "skills",
        "redrob_signals",
    ]

    # 1. Structural and presence checks
    for field in required_fields:
        if field not in candidate or candidate[field] is None:
            return False

    # 2. Type validation checks
    if not isinstance(candidate["candidate_id"], (str, int)):
        return False
    if not isinstance(candidate["profile"], dict):
        return False
    if not isinstance(candidate["career_history"], list):
        return False
    if not isinstance(candidate["education"], list):
        return False
    if not isinstance(candidate["skills"], list):
        return False
    if not isinstance(candidate["redrob_signals"], dict):
        return False

    return True


def stream_candidates(filepath: str) -> Generator[Dict, None, None]:
    """Memory-efficient generator that streams candidate profiles line-by-line.

    Supports both uncompressed (.jsonl) and gzipped (.jsonl.gz) files.
    Malformed rows or records that fail schema validation are skipped with warnings.

    Args:
        filepath (str): Path to the candidate pool data file.

    Yields:
        Generator[Dict, None, None]: Clean, validated candidate record dictionaries.

    Raises:
        FileNotFoundError: If the specified file does not exist on disk.
    """
    if not os.path.exists(filepath):
        logger.error("Data file '%s' was not found on disk.", filepath)
        raise FileNotFoundError(f"Candidate pool file not found: {filepath}")

    is_gzipped = filepath.endswith(".gz")
    open_func = gzip.open if is_gzipped else open
    mode = "rt" if is_gzipped else "r"

    logger.info("Starting candidate stream from '%s' (Gzip: %s)...", filepath, is_gzipped)
    
    line_idx = 0
    yielded_idx = 0
    
    try:
        with open_func(filepath, mode, encoding="utf-8") as f:
            for line in f:
                line_idx += 1
                if not line.strip():
                    continue

                try:
                    candidate = json.loads(line)
                except json.JSONDecodeError as e:
                    logger.warning(
                        "Skipping malformed JSON line %d in '%s': %s",
                        line_idx,
                        filepath,
                        str(e),
                    )
                    continue

                if not validate_candidate_schema(candidate):
                    logger.warning(
                        "Skipping candidate at line %d in '%s': Failed schema validation.",
                        line_idx,
                        filepath,
                    )
                    continue

                yielded_idx += 1
                yield candidate

        logger.info(
            "Stream closed. Read %d lines, yielded %d valid candidates.",
            line_idx,
            yielded_idx,
        )

    except Exception as e:
        logger.exception("Unexpected error encountered while streaming candidate data: %s", str(e))
        raise


def count_candidates(filepath: str) -> int:
    """Calculates the total row count of a candidate dataset in an efficient manner.

    Supports both uncompressed and gzipped data sources without loading files into RAM.

    Args:
        filepath (str): Path to the candidate pool data file.

    Returns:
        int: Total number of non-empty rows.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not os.path.exists(filepath):
        logger.error("Data file '%s' not found for counting.", filepath)
        raise FileNotFoundError(f"File not found: {filepath}")

    is_gzipped = filepath.endswith(".gz")
    open_func = gzip.open if is_gzipped else open
    mode = "rt" if is_gzipped else "r"

    logger.info("Counting candidates in '%s'...", filepath)
    count = 0

    try:
        with open_func(filepath, mode, encoding="utf-8") as f:
            # Efficient iteration counting lines
            for line in f:
                if line.strip():
                    count += 1

        logger.info("Completed count: %d candidates found in '%s'.", count, filepath)
        return count
    except Exception as e:
        logger.exception("Failed to count lines in candidate file: %s", str(e))
        raise


def load_job_description(filepath: str) -> str:
    """Reads and sanitizes the target job description file.

    Converts layout markup into a single normalized, clean string.

    Args:
        filepath (str): Path to the job description text file.

    Returns:
        str: Sanitized, normalized, lowercase string.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not os.path.exists(filepath):
        logger.error("Job description file '%s' not found on disk.", filepath)
        raise FileNotFoundError(f"Job description file not found: {filepath}")

    logger.info("Reading and cleaning job description from '%s'...", filepath)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        sanitized_content = sanitize_text(content)
        logger.info("Job description loaded successfully. Sanitized length: %d chars.", len(sanitized_content))
        return sanitized_content
    except Exception as e:
        logger.exception("Failed to read job description file: %s", str(e))
        raise
