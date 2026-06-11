import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import logging
from src.logger import PipelineLogger
from src.utils import parse_date, get_elapsed_days, sanitize_text, normalize_score, safe_divide
from src.config import load_config

def run_test():
    # 1. Initialize Logger
    logger = PipelineLogger.get_logger(log_file="logs/test_run.log")
    logger.info("Initializing Foundation Verification Test...")

    # 2. Load and verify Config
    try:
        config = load_config("configs/ranking_config.yaml")
        logger.info("Config pipeline date: %s", config.pipeline.current_date)
        logger.info("Config models model: %s", config.models.embedding_model)
        logger.info("Config retrieval top_k: %s", config.retrieval.stage1_top_k)
        logger.info("Config weights semantic: %s", config.weights.semantic_match)
        print("Config verification: SUCCESS")
    except Exception as e:
        logger.exception("Config verification failed: %s", str(e))
        print("Config verification: FAILED")
        return

    # 3. Verify utils
    try:
        # Date parsing
        d1 = parse_date("2026-06-04")
        d2 = parse_date("2026-06-01")
        days = get_elapsed_days(d2, d1)
        logger.info("Parsed dates: %s, %s. Difference: %s days.", d1, d2, days)
        assert days == 3, "get_elapsed_days failed"

        # Text Sanitizer
        raw_text = "  <p>Hello <b>World</b>!</p>   "
        clean_text = sanitize_text(raw_text)
        logger.info("Sanitized text: '%s'", clean_text)
        assert clean_text == "hello world !", f"sanitize_text failed: '{clean_text}'"

        # Normalization
        norm = normalize_score(7.5, 5.0, 10.0)
        logger.info("Normalized score: %s", norm)
        assert abs(norm - 0.5) < 1e-9, "normalize_score failed"

        # Safe divide
        div = safe_divide(10.0, 2.0)
        logger.info("Safe divide 10/2: %s", div)
        assert abs(div - 5.0) < 1e-9, "safe_divide standard failed"

        div_zero = safe_divide(10.0, 0.0, default=99.0)
        logger.info("Safe divide 10/0: %s", div_zero)
        assert abs(div_zero - 99.0) < 1e-9, "safe_divide by zero failed"
        
        print("Utils verification: SUCCESS")
    except Exception as e:
        logger.exception("Utils verification failed: %s", str(e))
        print("Utils verification: FAILED")
        return

    print("ALL TESTS COMPLETED SUCCESSFULLY!")

if __name__ == '__main__':
    run_test()
