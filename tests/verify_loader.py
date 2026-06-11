import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import os
import gzip
import json
from src.data_loader import stream_candidates, count_candidates, load_job_description, validate_candidate_schema

def run_test():
    print("Initializing DataLoader verification...")

    # 1. Create a mock candidate record
    mock_candidate = {
        "candidate_id": "CAND_9999999",
        "profile": {
            "anonymized_name": "Test Candidate",
            "years_of_experience": 5.0
        },
        "career_history": [],
        "education": [],
        "skills": [],
        "redrob_signals": {}
    }

    # Validate Schema check
    is_valid = validate_candidate_schema(mock_candidate)
    print(f"Validation of valid candidate: {is_valid} (Expected: True)")
    assert is_valid == True, "validate_candidate_schema failed on valid record"

    is_invalid = validate_candidate_schema({"candidate_id": "CAND_123"})
    print(f"Validation of invalid candidate: {is_invalid} (Expected: False)")
    assert is_invalid == False, "validate_candidate_schema failed on invalid record"

    # 2. Write a mock JSONL file
    temp_jsonl = "temp_test.jsonl"
    with open(temp_jsonl, "w", encoding="utf-8") as f:
        f.write(json.dumps(mock_candidate) + "\n")
        f.write("  \n")  # Empty line (should be skipped)
        f.write(json.dumps(mock_candidate) + "\n")
        f.write("{invalid json line}\n")  # Malformed line (should print warning and skip)

    # 3. Write a mock gzipped JSONL file
    temp_gz = "temp_test.jsonl.gz"
    with gzip.open(temp_gz, "wt", encoding="utf-8") as f:
        f.write(json.dumps(mock_candidate) + "\n")
        f.write(json.dumps(mock_candidate) + "\n")

    try:
        # Count JSONL
        count_jsonl = count_candidates(temp_jsonl)
        print(f"Count of '{temp_jsonl}': {count_jsonl} (Expected: 3)")
        assert count_jsonl == 3, "count_candidates failed on JSONL"

        # Count GZ
        count_gz = count_candidates(temp_gz)
        print(f"Count of '{temp_gz}': {count_gz} (Expected: 2)")
        assert count_gz == 2, "count_candidates failed on GZ"

        # Stream JSONL
        cands_jsonl = list(stream_candidates(temp_jsonl))
        print(f"Streamed candidate count from '{temp_jsonl}': {len(cands_jsonl)} (Expected: 2)")
        assert len(cands_jsonl) == 2, "stream_candidates failed on JSONL"

        # Stream GZ
        cands_gz = list(stream_candidates(temp_gz))
        print(f"Streamed candidate count from '{temp_gz}': {len(cands_gz)} (Expected: 2)")
        assert len(cands_gz) == 2, "stream_candidates failed on GZ"

        # Job Description load
        jd_file = "data/raw/job_description.txt"
        if os.path.exists(jd_file):
            jd_text = load_job_description(jd_file)
            print(f"Loaded Job Description: SUCCESS. Word count: {len(jd_text.split())}")
        else:
            print(f"Job Description file not found at '{jd_file}'. Skipping JD load test.")

        print("DataLoader verification: SUCCESS")
    finally:
        # Clean up temporary files
        if os.path.exists(temp_jsonl):
            os.remove(temp_jsonl)
        if os.path.exists(temp_gz):
            os.remove(temp_gz)

if __name__ == '__main__':
    run_test()
