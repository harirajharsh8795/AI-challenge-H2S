import os
import sys
import csv
import json

# Ensure workspace root is in path
workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(workspace_root)

# Import environment patches
import src.patch_env

from src.config import load_config
from src.data_loader import stream_candidates, load_job_description
from src.jd_parser import extract_requirements
from src.feature_engineering import extract_candidate_skills, build_feature_vector
from src.behavioral_scoring import compute_product_company_score, compute_behavioral_score, fuse_scores

def compile_data():
    config_path = os.path.join(workspace_root, "configs/ranking_config.yaml")
    jd_path = os.path.join(workspace_root, "data/raw/job_description.txt")
    candidates_path = os.path.join(workspace_root, "data/raw/candidates.jsonl")
    ranked_path = os.path.join(workspace_root, "data/processed/submission.csv")
    out_path = os.path.join(workspace_root, "frontend/src/utils/candidates_data.json")

    config = load_config(config_path)
    jd_text = load_job_description(jd_path)
    jd_spec = extract_requirements(jd_text)
    current_date = config.pipeline.current_date

    # 1. Read submission.csv
    ranked_ids = []
    ranked_meta = {}
    with open(ranked_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cid = row["candidate_id"]
            ranked_ids.append(cid)
            ranked_meta[cid] = {
                "rank": int(row["rank"]),
                "score": float(row["score"]),
                "reasoning": row["reasoning"]
            }

    # 2. Scan candidates pool
    candidates_db = {}
    for cand in stream_candidates(candidates_path):
        cid = cand.get("candidate_id")
        if cid:
            if isinstance(cid, int):
                cid_str = f"CAND_{cid:07d}"
            else:
                cid_str = str(cid).strip()
            
            if cid_str in ranked_meta:
                candidates_db[cid_str] = cand

    # 3. Assemble full profiles for Top 100
    assembled = []
    for cid in ranked_ids:
        cand = candidates_db.get(cid)
        meta = ranked_meta[cid]
        if not cand:
            continue

        profile = cand.get("profile", {}) or {}
        signals = cand.get("redrob_signals", {}) or {}
        
        # Experience
        y_exp = profile.get("years_of_experience", 0)
        try:
            y_exp_val = float(y_exp)
        except (ValueError, TypeError):
            y_exp_val = 0.0

        # Location
        location = profile.get("location", "N/A")

        # Notice period
        notice = signals.get("notice_period_days", 90)
        try:
            notice_val = int(notice)
        except (ValueError, TypeError):
            notice_val = 90

        # Response rate
        resp = signals.get("recruiter_response_rate", 0.0)
        try:
            resp_val = float(resp)
        except (ValueError, TypeError):
            resp_val = 0.0

        # Last active date and GitHub activity
        last_active = signals.get("last_active_date")
        from src.utils import parse_date, get_elapsed_days
        ref_date = parse_date(current_date)
        last_active_dt = parse_date(last_active) if last_active else None
        if last_active_dt and ref_date:
            active_days = get_elapsed_days(last_active_dt, ref_date)
        else:
            active_days = 180

        github = signals.get("github_activity_score", 0)
        try:
            github_val = int(github)
        except (ValueError, TypeError):
            github_val = 0

        open_to_work = signals.get("open_to_work_flag", True)

        # Company background
        product_score = compute_product_company_score(cand)
        if product_score == 1.0:
            company_bg = "Product"
        elif product_score == 0.0:
            company_bg = "Consulting"
        else:
            company_bg = "Mixed"

        # Skills
        cand_skills = extract_candidate_skills(cand)
        must_have = jd_spec.get("must_have", [])
        preferred = jd_spec.get("preferred", [])

        # Get overlap match
        from src.skill_graph import compute_skill_overlap
        must_overlap = compute_skill_overlap(cand_skills, must_have)
        pref_overlap = compute_skill_overlap(cand_skills, preferred)

        # Matched vs Expanded
        matched_must_have = [s for s in must_have if s.lower() in [c.lower() for c in cand_skills]]
        expanded_must_have = [s for s in must_have if s.lower() not in [c.lower() for c in cand_skills] and s.lower() in [k.lower() for k in must_overlap.get("expanded_matches", {}).keys()]]

        matched_pref = [s for s in preferred if s.lower() in [c.lower() for c in cand_skills]]

        # Features
        fv = build_feature_vector(cand, jd_spec)
        beh_score = compute_behavioral_score(cand, jd_spec, config)

        assembled.append({
          "candidate_id": cid,
          "rank": meta["rank"],
          "score": meta["score"],
          "headline": profile.get("headline", "N/A"),
          "years_of_experience": y_exp_val,
          "location": location,
          "notice_period_days": notice_val,
          "recruiter_response_rate": resp_val,
          "last_active_days": active_days,
          "github_activity_score": github_val,
          "open_to_work_flag": open_to_work,
          "company_background": company_bg,
          "must_have_skills": matched_must_have,
          "preferred_skills": matched_pref,
          "expanded_skills": expanded_must_have,
          "reasoning": meta["reasoning"],
          "breakdown": {
            "semantic_score": fv.get("semantic_score", 0.8),
            "experience_score": fv.get("experience_score", 1.0),
            "product_score": product_score,
            "behavioral_score": beh_score,
            "preferred_score": fv.get("preferred_skill_score", 0.0),
            "location_score": fv.get("location_score", 1.0),
            "must_have_score": fv.get("retrieval_skill_score", 0.0)
          }
        })

    # Save to JSON
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(assembled, f, indent=2)

    print(f"Compiled {len(assembled)} candidates profiles to {out_path}.")

if __name__ == "__main__":
    compile_data()
