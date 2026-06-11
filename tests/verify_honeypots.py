import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import logging
from datetime import date
from src.honeypots import normalize_company_name, is_consulting_only, is_honeypot

def run_test():
    print("Initializing Honeypot detection verification...")

    # 1. Test Company Normalization
    assert normalize_company_name("  Infosys  ") == "infosys"
    assert normalize_company_name("TCS  Group") == "tcs group"
    assert normalize_company_name(None) == ""
    assert normalize_company_name("") == ""
    assert normalize_company_name(123) == "" # non-string
    print("normalize_company_name: SUCCESS")

    # 2. Test Consulting Only
    consulting_cand = {
        "candidate_id": "CAND_00001",
        "career_history": [
            {"company": "TCS Ltd"},
            {"company": "  Infosys Limited  "},
            {"company": "Wipro Pvt Ltd"}
        ]
    }
    assert is_consulting_only(consulting_cand) == True
    
    mixed_cand = {
        "candidate_id": "CAND_00002",
        "career_history": [
            {"company": "TCS"},
            {"company": "Wayne Enterprises"}
        ]
    }
    assert is_consulting_only(mixed_cand) == False

    empty_cand = {
        "candidate_id": "CAND_00003",
        "career_history": []
    }
    assert is_consulting_only(empty_cand) == False
    assert is_consulting_only({}) == False
    print("is_consulting_only: SUCCESS")

    # 3. Test Honeypot Checks
    current_date = "2026-06-04"

    # Base Clean Candidate (Expected: False)
    clean_cand = {
        "candidate_id": "CAND_CLEAN",
        "profile": {"years_of_experience": 5.0},
        "skills": [
            {"name": "Python", "proficiency": "expert", "duration_months": 24}
        ],
        "career_history": [
            {"company": "Pied Piper", "start_date": "2022-06-04", "end_date": "2026-06-04", "duration_months": 48}
        ]
    }
    assert is_honeypot(clean_cand, current_date) == False

    # Rule 1 Honeypot: Skill proficiency expert with 0 duration
    rule1_cand = {
        "candidate_id": "CAND_R1",
        "skills": [
            {"name": "Python", "proficiency": "expert", "duration_months": 0}
        ]
    }
    assert is_honeypot(rule1_cand, current_date) == True

    # Rule 2 Honeypot: Duration mismatch (started in 2024, duration is 150 months)
    rule2_cand = {
        "candidate_id": "CAND_R2",
        "career_history": [
            {"company": "Wayne Enterprises", "start_date": "2024-06-04", "end_date": "2026-06-04", "duration_months": 150}
        ]
    }
    assert is_honeypot(rule2_cand, current_date) == True

    # Rule 3a Honeypot: Experience >= 1 but empty career history
    rule3a_cand = {
        "candidate_id": "CAND_R3A",
        "profile": {"years_of_experience": 5.0},
        "career_history": []
    }
    assert is_honeypot(rule3a_cand, current_date) == True

    # Rule 3b Honeypot: Experience gap (profile says 10 years, career has only 12 months = 1 year)
    rule3b_cand = {
        "candidate_id": "CAND_R3B",
        "profile": {"years_of_experience": 10.0},
        "career_history": [
            {"company": "Wayne Enterprises", "duration_months": 12}
        ]
    }
    assert is_honeypot(rule3b_cand, current_date) == True

    # Edge cases: Null parameters and missing structures (Should never crash)
    assert is_honeypot(None, current_date) == False
    assert is_honeypot({}, current_date) == False
    assert is_honeypot({"skills": None}, current_date) == False
    assert is_honeypot({"profile": None, "career_history": None}, current_date) == False

    # Numeric/Int candidate_id support
    int_id_cand = {
        "candidate_id": 999999,
        "profile": {"years_of_experience": 5.0},
        "career_history": []
    }
    assert is_honeypot(int_id_cand, current_date) == True # Flags Rule 3a correctly

    print("is_honeypot (Rule 1, 2, 3): SUCCESS")
    print("ALL TESTS COMPLETED SUCCESSFULLY!")

if __name__ == '__main__':
    run_test()
