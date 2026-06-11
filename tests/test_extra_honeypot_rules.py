import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import json

def scan():
    filepath = "data/raw/candidates.jsonl"
    flagged = {}
    
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            cand = json.loads(line)
            cid = cand.get("candidate_id")
            
            reasons = []
            prof = cand.get("profile", {})
            y_exp = prof.get("years_of_experience", 0)
            
            # Check skill duration vs profile experience
            skills = cand.get("skills", [])
            for sk in skills:
                name = sk.get("name")
                dur_months = sk.get("duration_months", 0)
                dur_years = dur_months / 12.0
                if dur_years > y_exp + 1.0: # Allowing 1 year buffer
                    reasons.append(f"Skill '{name}' duration ({dur_years:.2f} yrs) exceeds profile experience ({y_exp} yrs)")
            
            # Check education years vs current date
            edu_list = cand.get("education", [])
            for edu in edu_list:
                end = edu.get("end_year", 0)
                if end > 2026: # Education ending in future without current date match
                    # Wait, is it possible they are currently in school? If end_year is 2027, it might be fine, but if it is 2035?
                    if end > 2030:
                        reasons.append(f"Education end year ({end}) is too far in the future")
            
            if reasons:
                flagged[cid] = reasons
                
    print(f"Total candidates flagged with extra rules: {len(flagged)}")
    if flagged:
        print(f"Sample: {list(flagged.items())[:5]}")

if __name__ == '__main__':
    scan()
