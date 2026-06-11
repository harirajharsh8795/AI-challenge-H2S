import os
import sys
import csv
import json
import random
import math
from typing import Dict, List, Tuple

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
from evaluation_framework import calculate_dcg, calculate_ndcg, calculate_mrr, calculate_precision, calculate_recall

def get_independent_relevance(cand: Dict, jd_spec: Dict, current_date: str) -> float:
    # 1. Hard Disqualifications (Honeypot, Consulting Only)
    from src.honeypots import is_honeypot, is_consulting_only, is_technical_role
    if is_honeypot(cand, current_date):
        return 0.0
    if is_consulting_only(cand):
        return 0.0
    if not is_technical_role(cand):
        return 0.0

    profile = cand.get("profile", {}) or {}
    y_exp = profile.get("years_of_experience")
    if y_exp is None:
        return 0.0
    try:
        y_exp_val = float(y_exp)
    except (ValueError, TypeError):
        return 0.0

    if y_exp_val < 3.0 or y_exp_val > 12.0:
        return 0.0

    # 2. Continuous Experience Score (Target [5.0-9.0] = 1.0, decay outside)
    if 5.0 <= y_exp_val <= 9.0:
        exp_score = 1.0
    elif 3.0 <= y_exp_val < 5.0:
        exp_score = 0.5 + 0.25 * (y_exp_val - 3.0)  # 3.0 -> 0.5, 4.0 -> 0.75
    else:
        exp_score = 1.0 - 0.25 * (y_exp_val - 9.0)  # 10.0 -> 0.75, 11.0 -> 0.5, 12.0 -> 0.25

    # 3. Continuous Skill Coverage (must-have + preferred fraction)
    cand_skills = extract_candidate_skills(cand)
    must_have = jd_spec.get("must_have", [])
    preferred = jd_spec.get("preferred", [])
    total_skills = must_have + preferred
    
    if not total_skills:
        skill_score = 0.0
    else:
        matched = 0
        cand_skills_lower = [s.lower() for s in cand_skills]
        for s in total_skills:
            if s.lower() in cand_skills_lower:
                matched += 1
        skill_score = matched / len(total_skills)

    # 4. Product company background
    product_score = compute_product_company_score(cand)

    # 5. Continuous Availability (Notice period + login activity + response rate)
    signals = cand.get("redrob_signals", {}) or {}
    notice = signals.get("notice_period_days", 90)
    try:
        notice_val = float(notice)
    except (ValueError, TypeError):
        notice_val = 90.0
    notice_score = max(0.0, 1.0 - (notice_val / 90.0))

    resp = signals.get("recruiter_response_rate", 0.0)
    try:
        resp_score = float(resp)
    except (ValueError, TypeError):
        resp_score = 0.0

    last_active = signals.get("last_active_date")
    from src.utils import parse_date, get_elapsed_days
    ref_date = parse_date(current_date)
    last_active_dt = parse_date(last_active) if last_active else None
    if last_active_dt and ref_date:
        active_days = get_elapsed_days(last_active_dt, ref_date)
        activity_score = max(0.0, 1.0 - (active_days / 180.0))
    else:
        activity_score = 0.0
        
    avail_score = 0.4 * notice_score + 0.3 * resp_score + 0.3 * activity_score

    # Weighted blend: 25% Experience, 25% Skills, 20% Product, 15% Availability, 15% Semantic (simulated via match vector)
    fused_relevance = 0.25 * exp_score + 0.25 * skill_score + 0.20 * product_score + 0.15 * avail_score
    
    # Add minor semantic similarity approximation (Jaccard on text)
    summary = profile.get("summary", "")
    headline = profile.get("headline", "")
    text = (headline + " " + summary).lower()
    match_count = sum(1 for word in jd_spec.get("must_have", []) if word.lower() in text)
    sem_approx = match_count / max(1, len(jd_spec.get("must_have", [])))
    
    fused_relevance += 0.15 * sem_approx
    
    return min(1.0, fused_relevance)

def map_relevance_label(score: float) -> int:
    if score >= 0.60:
        return 2  # Strong Fit
    elif score >= 0.35:
        return 1  # Acceptable
    else:
        return 0  # Irrelevant

def run_independent_audit():
    config_path = os.path.join(workspace_root, "configs/ranking_config.yaml")
    jd_path = os.path.join(workspace_root, "data/raw/job_description.txt")
    candidates_path = os.path.join(workspace_root, "data/raw/candidates.jsonl")
    ranked_path = os.path.join(workspace_root, "data/processed/submission.csv")

    config = load_config(config_path)
    jd_text = load_job_description(jd_path)
    jd_spec = extract_requirements(jd_text)
    current_date = config.pipeline.current_date

    # 1. Load submission.csv
    ranked_ids = []
    with open(ranked_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ranked_ids.append(row["candidate_id"])

    # 2. Build ground truth on pool
    relevance_db = {}
    all_relevances = []
    
    for cand in stream_candidates(candidates_path):
        cid = cand.get("candidate_id")
        if cid:
            if isinstance(cid, int):
                cid_str = f"CAND_{cid:07d}"
            else:
                cid_str = str(cid).strip()
            score = get_independent_relevance(cand, jd_spec, current_date)
            label = map_relevance_label(score)
            relevance_db[cid_str] = label
            all_relevances.append(label)

    # Calculate metrics for the submission
    ranked_labels = [relevance_db.get(cid, 0) for cid in ranked_ids]
    ideal_labels = sorted(all_relevances, reverse=True)
    total_relevant = sum(1 for r in all_relevances if r >= 2)

    ndcg_10 = calculate_ndcg(ranked_labels, ideal_labels, 10)
    ndcg_100 = calculate_ndcg(ranked_labels, ideal_labels, 100)
    mrr = calculate_mrr(ranked_labels, 100, threshold=2)
    prec_10 = calculate_precision(ranked_labels, 10, threshold=2)
    prec_100 = calculate_precision(ranked_labels, 100, threshold=2)
    recall_100 = calculate_recall(ranked_labels, 100, total_relevant, threshold=2)

    print("\n" + "="*80)
    print("                    INDEPENDENT RELEVANCE AUDIT REPORT                  ")
    print("="*80)
    print(f"Total pool size: {len(all_relevances):,}")
    print(f"Pool relevance labels count: 0: {all_relevances.count(0):,}, 1: {all_relevances.count(1):,}, 2: {all_relevances.count(2):,}")
    print(f"Total independent strong fits (Rel=2) in pool: {total_relevant:,}")
    print("-"*80)
    print(f"Independent MRR:         {mrr:.4f}")
    print(f"Independent NDCG@10:     {ndcg_10:.4f}")
    print(f"Independent NDCG@100:    {ndcg_100:.4f}")
    print(f"Independent Prec@10:     {prec_10:.2%}")
    print(f"Independent Prec@100:    {prec_100:.2%}")
    print(f"Independent Recall@100:  {recall_100:.2%}")
    print("="*80)

    # 3. Robustness testing
    # Generate 5 perturbed weight sets
    print("\nRobustness Testing: Perturbing weights and measuring NDCG@100 stability...")
    print(f"{'Run':<6} | {'Weights (Sem/Exp/Prod/Beh/Pref/Loc)':<40} | {'NDCG@100':<10}")
    print("-" * 70)
    
    # We will simulate re-scoring candidates on perturbed weights
    # We load candidate detail feature vectors first (mocked from candidates in database)
    mock_shortlist_ids = ranked_ids
    # Let's read candidate profiles for the shortlist
    shortlist_cands = []
    for cid in mock_shortlist_ids:
        # We need their details. Since we have database cached, let's look them up.
        pass

    # Let's load the compiled candidates JSON to re-score them easily
    frontend_json_path = os.path.join(workspace_root, "frontend/src/utils/candidates_data.json")
    if os.path.exists(frontend_json_path):
        with open(frontend_json_path, "r", encoding="utf-8") as f:
            cands_json = json.load(f)
        
        for run_id in range(1, 6):
            # Perturb randomly
            w_sem = random.randint(20, 50)
            w_exp = random.randint(10, 25)
            w_prod = random.randint(10, 25)
            w_beh = random.randint(10, 25)
            w_pref = random.randint(5, 15)
            w_loc = random.randint(5, 15)
            total = w_sem + w_exp + w_prod + w_beh + w_pref + w_loc
            
            # Normalize to sum to 100
            w_sem = int((w_sem / total) * 100)
            w_exp = int((w_exp / total) * 100)
            w_prod = int((w_prod / total) * 100)
            w_beh = int((w_beh / total) * 100)
            w_pref = int((w_pref / total) * 100)
            w_loc = 100 - (w_sem + w_exp + w_prod + w_beh + w_pref)
            
            w_sem_f = w_sem / 100
            w_exp_f = w_exp / 100
            w_prod_f = w_prod / 100
            w_beh_f = w_beh / 100
            w_pref_f = w_pref / 100
            w_loc_f = w_loc / 100
            
            # Recalculate scores for shortlist candidates
            perturbed_ranked = []
            for c in cands_json:
                bk = c["breakdown"]
                fused = (
                    w_sem_f * bk["semantic_score"] +
                    w_exp_f * bk["experience_score"] +
                    w_prod_f * bk["product_score"] +
                    w_beh_f * bk["behavioral_score"] +
                    w_pref_f * bk["preferred_score"] +
                    w_loc_f * bk["location_score"]
                )
                if bk["must_have_score"] > 0.20:
                    fused += 0.25
                perturbed_ranked.append((fused, c["candidate_id"]))
            
            # Sort desc
            perturbed_ranked.sort(key=lambda x: (-x[0], x[1]))
            top_100_perturbed_ids = [x[1] for x in perturbed_ranked[:100]]
            
            # Compute NDCG@100
            perturbed_labels = [relevance_db.get(cid, 0) for cid in top_100_perturbed_ids]
            p_ndcg = calculate_ndcg(perturbed_labels, ideal_labels, 100)
            
            weights_str = f"{w_sem}/{w_exp}/{w_prod}/{w_beh}/{w_pref}/{w_loc}"
            print(f"Run {run_id:<2} | {weights_str:<40} | {p_ndcg:.4f}")

if __name__ == "__main__":
    run_independent_audit()
