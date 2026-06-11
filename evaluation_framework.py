import os
import sys
import csv
import argparse
import time
import math
from typing import Dict, List, Set, Tuple, Any

# Ensure current directory is on sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.config import load_config
from src.data_loader import stream_candidates, load_job_description
from src.jd_parser import extract_requirements
from src.honeypots import is_honeypot, is_consulting_only
from src.skill_graph import compute_skill_overlap
from src.feature_engineering import extract_candidate_skills, compute_location_score
from src.utils import parse_date


def compute_relevance_level(cand: Dict, jd_spec: Dict, current_date: Any) -> int:
    """Computes programmatic relevance level for a candidate based on JD criteria.

    Relevance Levels:
        0 = Irrelevant (Honeypot, Consulting-only, Experience out-of-bounds, or 0 must-have skill match)
        1 = Acceptable (Valid candidate, but outside target experience or low skill overlap)
        2 = Strong Fit (Matches ideal experience [5-9], has product exp, must-have overlap > 20%)
        3 = Ideal Fit (Strong fit + high responsiveness + immediate notice + location match + preferred skill)
    """
    cand_id = cand.get("candidate_id", "UNKNOWN")
    
    # 1. Hard Exclusions (Relevance = 0)
    if is_honeypot(cand, current_date):
        return 0
    if is_consulting_only(cand):
        return 0
        
    profile = cand.get("profile", {}) or {}
    y_exp = profile.get("years_of_experience")
    if y_exp is None:
        return 0
    try:
        y_exp_val = float(y_exp)
    except (ValueError, TypeError):
        return 0
        
    # Standard loose range [3.0, 12.0] for Acceptable, target range [5.0, 9.0] for Strong/Ideal
    if y_exp_val < 3.0 or y_exp_val > 12.0:
        return 0
        
    cand_skills = extract_candidate_skills(cand)
    must_have = jd_spec.get("must_have", [])
    
    # Compute skill overlap for must-have skills
    must_have_overlap = compute_skill_overlap(cand_skills, must_have)
    must_have_score = must_have_overlap.get("normalized_overlap_score", 0.0)
    
    if must_have_score == 0.0:
        return 0

    # 2. Check Strong Fit criteria (Relevance >= 2)
    # Target experience range is 5 to 9 years (inclusive)
    is_strong_exp = (5.0 <= y_exp_val <= 9.0)
    is_strong_skills = (must_have_score > 0.20)
    
    # Passes if they meet experience and skill thresholds
    if is_strong_exp and is_strong_skills:
        # Check Ideal Fit criteria (Relevance = 3)
        signals = cand.get("redrob_signals", {}) or {}
        
        # A. Login activity check (active within last 30 days)
        last_active = signals.get("last_active_date")
        is_active = False
        if last_active:
            last_active_dt = parse_date(last_active)
            ref_dt = parse_date(current_date) if isinstance(current_date, str) else current_date
            if last_active_dt and ref_dt:
                days_since_active = (ref_dt - last_active_dt).days
                is_active = (days_since_active <= 30)
                
        # B. Response rate check (>= 70%)
        response_rate = signals.get("recruiter_response_rate", 0.0)
        is_responsive = (response_rate >= 0.70)
        
        # C. Notice period check (<= 30 days)
        notice_days = signals.get("notice_period_days", 90)
        is_immediate = (notice_days <= 30)
        
        # D. Location preference check (Noida/Pune or Tier-1 Relocate)
        # We reuse the location score: Noida/Pune gives 1.0, Tier-1 gives 0.8, Relocation gives 0.6
        loc_score = compute_location_score(cand, jd_spec)
        is_loc_match = (loc_score >= 0.6)
        
        # E. Preferred skill check (at least one preferred skill matches)
        preferred = jd_spec.get("preferred", [])
        pref_overlap = compute_skill_overlap(cand_skills, preferred)
        pref_score = pref_overlap.get("normalized_overlap_score", 0.0)
        has_preferred_skill = (pref_score > 0.0)
        
        if is_active and is_responsive and is_immediate and is_loc_match and has_preferred_skill:
            return 3
        return 2

    # 3. Acceptable (Relevance = 1)
    return 1


def calculate_dcg(relevances: List[int], k: int) -> float:
    """Calculates Discounted Cumulative Gain (DCG) at K."""
    dcg = 0.0
    for i, rel in enumerate(relevances[:k]):
        # Formula: (2^rel - 1) / log2(i + 2)
        dcg += (2.0 ** rel - 1.0) / math.log2(i + 2.0)
    return dcg


def calculate_ndcg(ranked_relevances: List[int], ideal_relevances: List[int], k: int) -> float:
    """Calculates Normalized Discounted Cumulative Gain (NDCG) at K."""
    dcg = calculate_dcg(ranked_relevances, k)
    idcg = calculate_dcg(ideal_relevances, k)
    if idcg <= 0.0:
        return 0.0
    return dcg / idcg


def calculate_mrr(relevances: List[int], k: int, threshold: int = 2) -> float:
    """Calculates Mean Reciprocal Rank (MRR) at K.

    MRR is the reciprocal of the rank of the first relevant candidate (relevance >= threshold).
    """
    for i, rel in enumerate(relevances[:k]):
        if rel >= threshold:
            return 1.0 / (i + 1.0)
    return 0.0


def calculate_precision(relevances: List[int], k: int, threshold: int = 2) -> float:
    """Calculates Precision at K (proportion of top-K with relevance >= threshold)."""
    if k <= 0:
        return 0.0
    relevant_count = sum(1 for rel in relevances[:k] if rel >= threshold)
    return relevant_count / k


def calculate_recall(relevances: List[int], k: int, total_relevant_in_pool: int, threshold: int = 2) -> float:
    """Calculates Recall at K (proportion of total relevant in pool retrieved in top-K)."""
    if total_relevant_in_pool <= 0:
        return 0.0
    relevant_retrieved = sum(1 for rel in relevances[:k] if rel >= threshold)
    return relevant_retrieved / total_relevant_in_pool


def run_evaluation(
    candidates_path: str,
    jd_path: str,
    config_path: str,
    ranked_path: str
) -> Dict[str, Any]:
    """Runs the evaluation pipeline.

    Loads the full pool, assigns relevance, loads ranked submission, and computes metrics.
    """
    print(f"Loading configuration and parsing JD requirements...")
    config = load_config(config_path)
    jd_text = load_job_description(jd_path)
    jd_spec = extract_requirements(jd_text)
    
    current_date = config.pipeline.current_date
    print(f"Reference date: {current_date}")
    
    # 1. Generate programmatic ground truth over the entire candidate pool
    print("Ingesting candidate pool and generating ground truth relevance levels...")
    relevance_db: Dict[str, int] = {}
    rel_counts = {0: 0, 1: 0, 2: 0, 3: 0}
    
    start_time = time.time()
    for cand in stream_candidates(candidates_path):
        cand_id = cand.get("candidate_id")
        if cand_id:
            # Format candidate_id consistently to CAND_XXXXXXX
            if isinstance(cand_id, int):
                cand_id_str = f"CAND_{cand_id:07d}"
            else:
                cand_id_str = str(cand_id).strip()
                
            rel = compute_relevance_level(cand, jd_spec, current_date)
            relevance_db[cand_id_str] = rel
            rel_counts[rel] += 1
            
    elapsed = time.time() - start_time
    total_candidates = len(relevance_db)
    print(f"Processed {total_candidates:,} candidate profiles in {elapsed:.2f} seconds.")
    print(f"Ground Truth Distribution:")
    print(f"  - Relevance 0 (Irrelevant): {rel_counts[0]:,} ({rel_counts[0]/total_candidates*100:.2f}%)")
    print(f"  - Relevance 1 (Acceptable):  {rel_counts[1]:,} ({rel_counts[1]/total_candidates*100:.2f}%)")
    print(f"  - Relevance 2 (Strong Fit):  {rel_counts[2]:,} ({rel_counts[2]/total_candidates*100:.2f}%)")
    print(f"  - Relevance 3 (Ideal Fit):   {rel_counts[3]:,} ({rel_counts[3]/total_candidates*100:.2f}%)")
    
    # 2. Load the pipeline's ranked submission output
    print(f"Loading ranked candidates from '{ranked_path}'...")
    ranked_ids: List[str] = []
    try:
        with open(ranked_path, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            # Find candidate_id index
            cid_idx = header.index("candidate_id")
            for row in reader:
                if row:
                    ranked_ids.append(row[cid_idx].strip())
    except Exception as e:
        print(f"ERROR: Failed to read submission file: {e}", file=sys.stderr)
        sys.exit(1)
        
    print(f"Loaded {len(ranked_ids)} ranked candidates from submission file.")
    
    # Map ranked candidates to their ground truth relevance levels
    ranked_relevances = []
    honeypot_count_in_top_100 = 0
    consulting_count_in_top_100 = 0
    
    for i, cid in enumerate(ranked_ids):
        rel = relevance_db.get(cid, 0)
        ranked_relevances.append(rel)
        
        # Double check if any honeypot or consulting bypassed the filters
        # In our relevance definition, honeypots and consulting have relevance 0.
        # Let's inspect them for specific audit feedback.
        if rel == 0:
            # We can log if it is indeed a honeypot
            pass

    # 3. Calculate ideal relevance distribution for NDCG (IDCG)
    all_relevances = list(relevance_db.values())
    ideal_relevances = sorted(all_relevances, reverse=True)
    
    # Total relevant in the pool (threshold >= 2)
    total_relevant_in_pool = sum(1 for r in all_relevances if r >= 2)
    print(f"Total relevant candidates (Relevance >= 2) in entire pool: {total_relevant_in_pool:,}")
    
    # 4. Calculate metrics
    ndcg_10 = calculate_ndcg(ranked_relevances, ideal_relevances, 10)
    ndcg_100 = calculate_ndcg(ranked_relevances, ideal_relevances, 100)
    mrr = calculate_mrr(ranked_relevances, 100, threshold=2)
    precision_10 = calculate_precision(ranked_relevances, 10, threshold=2)
    precision_100 = calculate_precision(ranked_relevances, 100, threshold=2)
    recall_100 = calculate_recall(ranked_relevances, 100, total_relevant_in_pool, threshold=2)
    
    report = {
        "metrics": {
            "NDCG@10": ndcg_10,
            "NDCG@100": ndcg_100,
            "MRR": mrr,
            "Precision@10": precision_10,
            "Precision@100": precision_100,
            "Recall@100": recall_100
        },
        "distribution": rel_counts,
        "ranked_relevances": ranked_relevances[:100]
    }
    
    return report


def print_evaluation_report(report: Dict[str, Any]):
    """Prints a styled, recruiter-friendly evaluation report."""
    metrics = report["metrics"]
    print("\n" + "="*80)
    print("                    REDROB RETRIEVAL EVALUATION REPORT                  ")
    print("="*80)
    print(f"{'Metric':<25} | {'Score':<10} | {'Interpretation'}")
    print("-"*80)
    print(f"{'NDCG@10':<25} | {metrics['NDCG@10']:<10.4f} | Ideal ranking alignment in Top 10")
    print(f"{'NDCG@100':<25} | {metrics['NDCG@100']:<10.4f} | Ideal ranking alignment in Top 100")
    print(f"{'MRR':<25} | {metrics['MRR']:<10.4f} | Reciprocal rank of first strong/ideal candidate")
    print(f"{'Precision@10':<25} | {metrics['Precision@10']:<10.2%} | Proportion of strong/ideal in Top 10")
    print(f"{'Precision@100':<25} | {metrics['Precision@100']:<10.2%} | Proportion of strong/ideal in Top 100")
    print(f"{'Recall@100':<25} | {metrics['Recall@100']:<10.2%} | Recall rate of all pool strong/ideal candidates")
    print("="*80)
    
    # Print ranked candidate relevance levels preview
    relevances = report["ranked_relevances"]
    print("Ranked List Relevance Preview (Top 100 Candidates):")
    row_str = ""
    for idx, rel in enumerate(relevances):
        row_str += f"R{idx+1:02d}:{rel} "
        if (idx + 1) % 10 == 0:
            print(f"  {row_str}")
            row_str = ""
    print("="*80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Redrob Candidate Discovery Evaluation Framework")
    parser.add_argument(
        "--candidates",
        type=str,
        default="data/raw/candidates.jsonl",
        help="Path to full candidates.jsonl file"
    )
    parser.add_argument(
        "--jd",
        type=str,
        default="data/raw/job_description.txt",
        help="Path to job description text file"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="configs/ranking_config.yaml",
        help="Path to config file"
    )
    parser.add_argument(
        "--ranked",
        type=str,
        default="data/processed/submission.csv",
        help="Path to generated submission.csv file"
    )
    
    args = parser.parse_args()
    
    # Check if files exist
    for filepath in [args.candidates, args.jd, args.config, args.ranked]:
        if not os.path.exists(filepath):
            print(f"ERROR: File not found: {filepath}", file=sys.stderr)
            sys.exit(1)
            
    print(f"Running evaluation on '{args.ranked}' against candidates pool '{args.candidates}'...")
    try:
        report = run_evaluation(
            candidates_path=args.candidates,
            jd_path=args.jd,
            config_path=args.config,
            ranked_path=args.ranked
        )
        print_evaluation_report(report)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"FATAL: Evaluation framework failed with error: {e}", file=sys.stderr)
        sys.exit(1)
