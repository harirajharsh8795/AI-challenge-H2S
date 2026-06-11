import os
import sys
import csv
import re
import time
import argparse
import unittest
from io import StringIO
from typing import List, Tuple, Dict, Any, Set


# Regex pattern matching standard candidate_id format (e.g. CAND_0000001)
CANDIDATE_ID_PATTERN = re.compile(r"^CAND_[0-9]{7}$")


def validate_submission_file(filepath: str) -> Tuple[bool, List[str]]:
    """Validates the submission CSV file against the hackathon rules.

    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_error_messages)
    """
    errors: List[str] = []
    
    if not os.path.exists(filepath):
        return False, [f"File not found: {filepath}"]
        
    try:
        with open(filepath, mode="r", encoding="utf-8", newline="") as f:
            content = f.read()
    except Exception as e:
        return False, [f"Failed to read file: {e}"]
        
    return validate_submission_content(content)


def validate_submission_content(csv_content: str) -> Tuple[bool, List[str]]:
    """Validates the CSV content string against the hackathon rules."""
    errors: List[str] = []
    
    # Check for empty file
    if not csv_content.strip():
        return False, ["CSV file is empty."]
        
    # Parse CSV content
    reader = csv.reader(StringIO(csv_content.strip()))
    
    # 1. Header Validation
    try:
        headers = next(reader)
    except StopIteration:
        return False, ["CSV file has no header row."]
        
    expected_headers = ["candidate_id", "rank", "score", "reasoning"]
    normalized_headers = [h.strip().lower() for h in headers]
    
    if normalized_headers != expected_headers:
        errors.append(
            f"Invalid headers. Expected {expected_headers}, got {headers}."
        )
        # Stop early if headers are broken since column indexes will be invalid
        return False, errors
        
    rows: List[List[str]] = []
    line_number = 1  # Header is line 1
    
    for row in reader:
        line_number += 1
        if not row:
            # Skip empty lines
            continue
            
        # 2. Column Count Validation
        if len(row) != 4:
            errors.append(
                f"Line {line_number}: Incorrect column count. Expected 4, got {len(row)}."
            )
            continue
            
        rows.append(row)
        
    # 3. Row Count Validation
    total_candidates = len(rows)
    if total_candidates != 100:
        errors.append(
            f"Incorrect number of candidates. Expected exactly 100, got {total_candidates}."
        )
        
    # 4. Fields Validation Loop
    seen_ids: Set[str] = set()
    prev_score = float("inf")
    
    for idx, row in enumerate(rows):
        line_num = idx + 2  # 1-indexed, skipping header
        cand_id, rank_str, score_str, reasoning = row
        
        # A. Candidate ID validation
        cand_id = cand_id.strip()
        if not cand_id:
            errors.append(f"Line {line_num}: Empty candidate_id.")
        elif not CANDIDATE_ID_PATTERN.match(cand_id):
            errors.append(
                f"Line {line_num}: Invalid candidate_id format '{cand_id}'. Must match CAND_XXXXXXX."
            )
            
        # Duplicate detection
        if cand_id in seen_ids:
            errors.append(f"Line {line_num}: Duplicate candidate_id '{cand_id}'.")
        seen_ids.add(cand_id)
        
        # B. Rank sequence validation
        try:
            rank_val = int(rank_str.strip())
            expected_rank = idx + 1
            if rank_val != expected_rank:
                errors.append(
                    f"Line {line_num}: Invalid rank sequence. Expected {expected_rank}, got {rank_val}."
                )
        except ValueError:
            errors.append(
                f"Line {line_num}: Rank '{rank_str}' is not an integer."
            )
            
        # C. Score monotonicity validation
        try:
            score_val = float(score_str.strip())
            if score_val > prev_score:
                errors.append(
                    f"Line {line_num}: Score '{score_val}' violates descending order. Previous score was '{prev_score}'."
                )
            prev_score = score_val
        except ValueError:
            errors.append(
                f"Line {line_num}: Score '{score_str}' is not a valid float."
            )
            
        # D. Reasoning validation
        reasoning = reasoning.strip()
        if not reasoning:
            errors.append(f"Line {line_num}: Empty reasoning column.")
        elif len(reasoning) < 10:
            errors.append(
                f"Line {line_num}: Reasoning string '{reasoning}' is too short (must be >= 10 chars)."
            )
            
    is_valid = len(errors) == 0
    return is_valid, errors


# ==============================================================================
# SELF-TEST UNIT SUITE
# ==============================================================================
class TestSubmissionValidator(unittest.TestCase):
    
    def setUp(self):
        # Generate a perfectly valid CSV content with 100 candidates
        valid_rows = ["candidate_id,rank,score,reasoning"]
        for i in range(1, 101):
            valid_rows.append(
                f"CAND_{i:07d},{i},{1.0 - (i*0.005):.4f},Verified candidate matching core criteria details."
            )
        self.valid_csv = "\n".join(valid_rows)

    def test_valid_csv(self):
        is_valid, errors = validate_submission_content(self.valid_csv)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_invalid_header(self):
        invalid_header = self.valid_csv.replace("candidate_id,rank,score,reasoning", "candidate,rank,score,reasoning")
        is_valid, errors = validate_submission_content(invalid_header)
        self.assertFalse(is_valid)
        self.assertIn("Invalid headers", errors[0])

    def test_incorrect_row_count(self):
        # Remove last row (now has 99 candidates)
        lines = self.valid_csv.split("\n")[:-1]
        broken_csv = "\n".join(lines)
        is_valid, errors = validate_submission_content(broken_csv)
        self.assertFalse(is_valid)
        self.assertTrue(any("Incorrect number of candidates" in err for err in errors))

    def test_duplicate_candidate_id(self):
        # Replace candidate 2 with candidate 1 ID
        broken_csv = self.valid_csv.replace("CAND_0000002", "CAND_0000001")
        is_valid, errors = validate_submission_content(broken_csv)
        self.assertFalse(is_valid)
        self.assertTrue(any("Duplicate candidate_id" in err for err in errors))

    def test_invalid_candidate_id_format(self):
        # Replace candidate 1 ID with invalid format
        broken_csv = self.valid_csv.replace("CAND_0000001", "CAND_1")
        is_valid, errors = validate_submission_content(broken_csv)
        self.assertFalse(is_valid)
        self.assertTrue(any("Invalid candidate_id format" in err for err in errors))

    def test_broken_rank_sequence(self):
        # Replace rank 2 with rank 99
        broken_csv = self.valid_csv.replace("CAND_0000002,2,", "CAND_0000002,99,")
        is_valid, errors = validate_submission_content(broken_csv)
        self.assertFalse(is_valid)
        self.assertTrue(any("Invalid rank sequence" in err for err in errors))

    def test_broken_score_monotonicity(self):
        # Replace score 2 with 2.0 (higher than candidate 1 score of 0.995)
        broken_csv = self.valid_csv.replace("CAND_0000002,2,0.9900,", "CAND_0000002,2,2.0000,")
        is_valid, errors = validate_submission_content(broken_csv)
        self.assertFalse(is_valid)
        self.assertTrue(any("violates descending order" in err for err in errors))

    def test_empty_reasoning(self):
        # Replace candidate 1 reasoning with empty string
        broken_csv = self.valid_csv.replace(",Verified candidate matching core criteria details.", ", ")
        is_valid, errors = validate_submission_content(broken_csv)
        self.assertFalse(is_valid)
        self.assertTrue(any("Empty reasoning column" in err for err in errors))

    def test_corrupt_columns(self):
        # Create a line with missing columns
        lines = self.valid_csv.split("\n")
        lines[10] = "CAND_0000010,10"  # Missing score and reasoning
        broken_csv = "\n".join(lines)
        is_valid, errors = validate_submission_content(broken_csv)
        self.assertFalse(is_valid)
        self.assertTrue(any("Incorrect column count" in err for err in errors))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Redrob Submission CSV Format Validator")
    parser.add_argument(
        "--file",
        type=str,
        default="data/processed/submission.csv",
        help="Path to submission CSV file to validate"
    )
    parser.add_argument(
        "--run-tests",
        action="store_true",
        help="Runs self-testing unit tests on the validator code"
    )
    
    args = parser.parse_args()
    
    if args.run_tests:
        print("Running self-contained submission validator tests...")
        # Remove CLI arguments so unittest doesn't try to parse them
        sys.argv = sys.argv[:1]
        unittest.main()
        sys.exit(0)
        
    print(f"Validating submission file '{args.file}'...")
    start_time = time.time()
    
    is_valid, errors = validate_submission_file(args.file)
    elapsed = time.time() - start_time
    
    print("\n" + "="*80)
    print("                    REDROB SUBMISSION VALIDATION REPORT                  ")
    print("="*80)
    print(f"File Target: {args.file}")
    print(f"Runtime:     {elapsed*1000:.3f} ms")
    
    if is_valid:
        print("Status:      [PASS]")
        print("Summary:     Submission matches all format, rank, score, and column schemas.")
        print("="*80)
        sys.exit(0)
    else:
        print("Status:      [FAIL]")
        print(f"Summary:     Found {len(errors)} format validation violations.")
        print("-"*80)
        print("Errors list:")
        # Print top 15 errors to prevent terminal flooding
        for idx, err in enumerate(errors[:15]):
            print(f"  {idx+1:02d}. [VIOLATION] {err}")
        if len(errors) > 15:
            print(f"  ... and {len(errors) - 15} more violations.")
        print("="*80)
        sys.exit(1)

