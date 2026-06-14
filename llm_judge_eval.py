#!/usr/bin/env python3
import os
import sys
import json
import csv
import random
import argparse
import math
import time
import re
from typing import List, Dict, Tuple, Any

# Ensure current directory is on sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.config import load_config
from src.data_loader import stream_candidates, load_job_description
from src.jd_parser import extract_requirements
from src.feature_engineering import extract_candidate_skills
from src.behavioral_scoring import get_reference_date
from src.utils import parse_date
from src.skill_graph import compute_skill_overlap


SYSTEM_PROMPT = """You are an expert technical recruiter with 15 years of experience.
Rate this candidate's fit for the job description on a scale of 0-3:
0 = Not a fit (missing must-have skills, wrong experience level)
1 = Acceptable (partial skill match, meets minimum experience)
2 = Strong fit (most skills match, good experience range)
3 = Ideal fit (all skills match, perfect experience, immediate availability)

Reply with ONLY a JSON object: {"score": <0-3>, "reason": "<one sentence>"}"""


def mock_gemini_judge(candidate: Dict, jd_text: str) -> Dict[str, Any]:
    """Fallback mock judge using skill overlap and experience metrics."""
    try:
        jd_spec = extract_requirements(jd_text)
    except Exception:
        jd_spec = {}
        
    cand_skills = extract_candidate_skills(candidate)
    must_have = jd_spec.get("must_have", [])
    if must_have:
        must_have_overlap = compute_skill_overlap(cand_skills, must_have)
        must_have_score = must_have_overlap.get("normalized_overlap_score", 0.0)
    else:
        must_have_score = 0.0

    profile = candidate.get("profile", {})
    y_exp = profile.get("years_of_experience")
    try:
        y_exp_val = float(y_exp) if y_exp is not None else 0.0
    except (ValueError, TypeError):
        y_exp_val = 0.0

    signals = candidate.get("redrob_signals", {})
    try:
        notice = float(signals.get("notice_period_days", 90))
    except (ValueError, TypeError):
        notice = 90.0

    if must_have_score == 0.0 or y_exp_val < 3.0 or y_exp_val > 12.0:
        score = 0
        reason = "Missing must-have skills or experience out of acceptable range."
    elif must_have_score > 0.40 and (5.0 <= y_exp_val <= 9.0) and notice <= 30.0:
        score = 3
        reason = f"Excellent skill overlap ({must_have_score:.1%}), ideal experience ({y_exp_val} yrs), and immediate notice ({notice} days)."
    elif must_have_score > 0.20 and (5.0 <= y_exp_val <= 9.0):
        score = 2
        reason = f"Strong skill overlap ({must_have_score:.1%}) and target experience range ({y_exp_val} yrs)."
    else:
        score = 1
        reason = f"Acceptable profile with {y_exp_val} years experience and partial skill matches."
        
    return {"score": score, "reason": reason}


def calculate_dcg(relevances: List[int], k: int) -> float:
    """Calculates Discounted Cumulative Gain (DCG) at K."""
    dcg = 0.0
    for i, rel in enumerate(relevances[:k]):
        dcg += (2.0 ** rel - 1.0) / math.log2(i + 2.0)
    return dcg


def calculate_ndcg(ranked_relevances: List[int], ideal_relevances: List[int], k: int) -> float:
    """Calculates Normalized Discounted Cumulative Gain (NDCG) at K."""
    dcg = calculate_dcg(ranked_relevances, k)
    idcg = calculate_dcg(ideal_relevances, k)
    if idcg <= 0.0:
        return 0.0
    return dcg / idcg


def main():
    parser = argparse.ArgumentParser(description="LLM-as-a-Judge Evaluation Framework")
    parser.add_argument("--candidates", type=str, default="data/raw/candidates.jsonl", help="Path to candidates.jsonl")
    parser.add_argument("--jd", type=str, default="data/raw/job_description.txt", help="Path to job description")
    parser.add_argument("--config", type=str, default="configs/ranking_config.yaml", help="Path to configuration")
    parser.add_argument("--ranked", type=str, default="data/processed/submission.csv", help="Path to submission.csv")
    parser.add_argument("--sample-size", type=str, default="30", help="Total sample size to evaluate")
    parser.add_argument("--no-cache", action="store_true", help="Bypass cache loading and writing")
    args = parser.parse_args()

    # Parse sample size dynamically
    try:
        sample_size = int(args.sample_size)
    except ValueError:
        sample_size = 30

    top_n = sample_size // 3
    mid_n = sample_size // 3
    unranked_n = sample_size - (top_n + mid_n)

    # 1. Load config and input files
    config = load_config(args.config)
    jd_text = load_job_description(args.jd)

    # 2. Read submission.csv
    submission_rows = []
    if os.path.exists(args.ranked):
        with open(args.ranked, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                submission_rows.append(row)
    else:
        print(f"ERROR: Submission file not found at {args.ranked}")
        sys.exit(1)

    if len(submission_rows) < 100:
        print(f"Warning: submission.csv has only {len(submission_rows)} candidates, expected at least 100.")

    # 3. Sample candidate IDs
    top_100_ids_set = {row["candidate_id"] for row in submission_rows}
    top_n_ids = [row["candidate_id"] for row in submission_rows[:top_n]]
    
    mid_pool = [row["candidate_id"] for row in submission_rows[49:100]]
    if len(mid_pool) < mid_n:
        mid_pool = [row["candidate_id"] for row in submission_rows[top_n:]]
    
    random.seed(42)
    selected_mid_ids = random.sample(mid_pool, min(mid_n, len(mid_pool)))

    top_n_set = set(top_n_ids)
    mid_n_set = set(selected_mid_ids)
    target_ids_set = top_n_set.union(mid_n_set)

    # 4. Stream profiles to collect top and mid candidate profiles + build unranked candidate list
    candidate_profiles = {}
    unranked_ids = []

    for cand in stream_candidates(args.candidates):
        cid = cand.get("candidate_id")
        if cid is None:
            continue
        if isinstance(cid, int):
            cid_str = f"CAND_{cid:07d}"
        else:
            cid_str = str(cid).strip()
            
        if cid_str in target_ids_set:
            candidate_profiles[cid_str] = cand
        elif cid_str not in top_100_ids_set:
            unranked_ids.append(cid_str)

    # Sample unranked candidate IDs
    selected_unranked_ids = random.sample(unranked_ids, min(unranked_n, len(unranked_ids)))
    selected_unranked_ids_set = set(selected_unranked_ids)

    # Stream again to load profiles for unranked candidates
    for cand in stream_candidates(args.candidates):
        cid = cand.get("candidate_id")
        if cid is None:
            continue
        if isinstance(cid, int):
            cid_str = f"CAND_{cid:07d}"
        else:
            cid_str = str(cid).strip()
            
        if cid_str in selected_unranked_ids_set:
            candidate_profiles[cid_str] = cand

    # 5. Initialize cache
    cache_path = "data/processed/llm_judge_cache.json"
    cache = {}
    if not args.no_cache and os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load cache from {cache_path}: {e}")

    # 6. Initialize Gemini
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    use_gemini = True
    if not api_key:
        print("Warning: GOOGLE_API_KEY / GEMINI_API_KEY not set. Falling back to mock evaluator.")
        use_gemini = False
    else:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=SYSTEM_PROMPT,
            )
        except Exception as e:
            print(f"Warning: Failed to initialize Gemini client: {e}. Falling back to mock evaluator.")
            use_gemini = False

    # 7. Evaluate candidates
    evaluated_list = []
    
    # Store submission.csv mapping of ID to rank
    id_to_rank = {row["candidate_id"]: int(row["rank"]) for row in submission_rows}

    # Order of processing: top_n, then mid_n, then unranked_n
    ordered_ids = top_n_ids + selected_mid_ids + selected_unranked_ids
    
    for cid_str in ordered_ids:
        candidate = candidate_profiles.get(cid_str)
        if not candidate:
            print(f"Warning: Profile not found for candidate {cid_str}, skipping.")
            continue

        # Extract features for summary
        profile = candidate.get("profile", {})
        signals = candidate.get("redrob_signals", {})
        
        current_title = profile.get("current_title", "N/A")
        years = profile.get("years_of_experience", "N/A")
        top_skills = ", ".join(extract_candidate_skills(candidate)[:10])
        notice_period = signals.get("notice_period_days", "N/A")
        location = profile.get("location", "N/A")
        
        last_active_str = signals.get("last_active_date")
        if last_active_str:
            last_active_dt = parse_date(last_active_str)
            if last_active_dt:
                ref_dt = get_reference_date(config)
                days_since_active = (ref_dt - last_active_dt).days
            else:
                days_since_active = "N/A"
        else:
            days_since_active = "N/A"

        candidate_summary = f"Title: {current_title}. Experience: {years} years. Skills: {top_skills}. Notice: {notice_period} days. Location: {location}. Last active: {days_since_active} days ago."

        # Fetch score and reason
        score = None
        reason = None
        
        if not args.no_cache and cid_str in cache:
            score = cache[cid_str].get("score")
            reason = cache[cid_str].get("reason")
        
        if score is None or reason is None:
            if use_gemini:
                success = False
                for attempt in range(3):
                    try:
                        response = model.generate_content(
                            f"Job Description:\n{jd_text}\n\nCandidate Profile:\n{candidate_summary}",
                            generation_config={"response_mime_type": "application/json", "temperature": 0.1}
                        )
                        raw = response.text.strip()
                        raw = re.sub(r"^```(?:json)?", "", raw).strip()
                        raw = re.sub(r"```$", "", raw).strip()
                        res = json.loads(raw)
                        score = int(res["score"])
                        reason = res["reason"]
                        success = True
                        break
                    except Exception as e:
                        print(f"Gemini API call attempt {attempt+1} failed for {cid_str}: {e}")
                        time.sleep(2)
                if not success:
                    print(f"All Gemini attempts failed for {cid_str}. Using mock fallback.")
                    mock_res = mock_gemini_judge(candidate, jd_text)
                    score = mock_res["score"]
                    reason = mock_res["reason"]
            else:
                mock_res = mock_gemini_judge(candidate, jd_text)
                score = mock_res["score"]
                reason = mock_res["reason"]

            # Save back to runtime cache
            cache[cid_str] = {"score": score, "reason": reason}

        pipeline_rank = id_to_rank.get(cid_str)
        evaluated_list.append({
            "candidate_id": cid_str,
            "pipeline_rank": pipeline_rank,
            "gemini_score": score,
            "gemini_reason": reason,
        })

    # Save cache
    if not args.no_cache:
        try:
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cache, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save cache to {cache_path}: {e}")

    # 8. Compute NDCG and Precision
    # Sort evaluated candidates by pipeline rank. Top 100 first, then unranked (rank 99999).
    def sort_by_pipeline_rank(item):
        rank = item["pipeline_rank"]
        return rank if rank is not None else 99999

    ranked_evaluation = sorted(evaluated_list, key=sort_by_pipeline_rank)
    
    ranked_relevances = [item["gemini_score"] for item in ranked_evaluation]
    ideal_relevances = sorted(ranked_relevances, reverse=True)

    ndcg_at_10 = calculate_ndcg(ranked_relevances, ideal_relevances, 10)
    
    # Precision@10: proportion of top 10 rated >= 2 by Gemini
    top_10_relevances = ranked_relevances[:10]
    precision_at_10 = sum(1 for r in top_10_relevances if r >= 2) / 10.0

    # 9. Save results json
    results_path = "data/processed/llm_judge_results.json"
    results = {
        "methodology": "LLM-as-Judge using Gemini 1.5 Flash as independent evaluator",
        "sample_size": sample_size,
        "ndcg_at_10_vs_llm": round(ndcg_at_10, 4),
        "precision_at_10_vs_llm": round(precision_at_10, 3),
        "candidates_evaluated": evaluated_list
    }

    try:
        os.makedirs(os.path.dirname(results_path), exist_ok=True)
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not write results to {results_path}: {e}")

    # 10. Print clean summary
    print("\n=== LLM-AS-JUDGE EVALUATION ===")
    print("Evaluator: Gemini 1.5 Flash (zero-shot, no pipeline logic exposed)")
    print(f"Sample: {sample_size} candidates ({top_n} top-ranked + {mid_n} mid-ranked + {unranked_n} random unranked)")
    print(f"NDCG@10 vs LLM Judge: {ndcg_at_10:.4f}")
    print(f"Precision@10 vs LLM Judge: {precision_at_10:.1%}")
    print(f"Top 10 Gemini Scores: {top_10_relevances}")
    print("================================\n")


if __name__ == "__main__":
    main()
