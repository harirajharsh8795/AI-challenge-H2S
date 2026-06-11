import os
import sys

# Ensure parent directory of src/ is on sys.path for direct file execution
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Apply critical environment patches (numpy, scipy, pyarrow) first
import src.patch_env

import time
import argparse
import csv
import logging
from typing import Dict, List, Tuple, Optional, Any



# ==============================================================================
# PIPELINE SYSPATH INTEGRATION
# ==============================================================================
# Ensure parent directory of src/ is on sys.path for direct file execution
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# ==============================================================================
# PIPELINE COMPONENT IMPORTS
# ==============================================================================
from src.logger import PipelineLogger
from src.config import load_config, AppConfig
from src.data_loader import stream_candidates, load_job_description
from src.jd_parser import extract_requirements
from src.honeypots import is_honeypot, is_consulting_only, is_technical_role
from src.feature_engineering import extract_candidate_skills, build_feature_vector
import src.feature_engineering as fe
from src.skill_graph import compute_skill_overlap
from src.retrieval import retrieve_top_candidates
from src.semantic_reranker import rerank_candidates as semantic_rerank
from src.cross_encoder_reranker import rerank_candidates as cross_encoder_rerank
from src.behavioral_scoring import rank_candidates as final_rank
from src.explainability import generate_candidate_reasoning

# Initialize central logging channel
logger = PipelineLogger.get_logger()

# ==============================================================================
# STAGE 1: SKILL GRAPH INTEGRATION (MONKEYPATCH FOR HIGHEST ROI COHERENCE)
# ==============================================================================
# Dynamically binds BFS Graph-based expansion overlap checks to the Pydantic-driven
# feature engineering scoring pipeline. This guarantees that synonym expansion and
# decay factors are accounted for during the behavioral score fusion step.
def skill_graph_retrieval_score(candidate: Dict, jd_spec: Dict) -> float:
    """Calculates semantic overlap of must-have skills using BFS Skill Graph."""
    candidate_skills = extract_candidate_skills(candidate)
    must_have = jd_spec.get("must_have", [])
    if not must_have:
        return 0.0
    overlap = compute_skill_overlap(candidate_skills, must_have)
    return float(overlap["normalized_overlap_score"])

def skill_graph_preferred_score(candidate: Dict, jd_spec: Dict) -> float:
    """Calculates semantic overlap of preferred skills using BFS Skill Graph."""
    candidate_skills = extract_candidate_skills(candidate)
    preferred = jd_spec.get("preferred", [])
    if not preferred:
        return 0.0
    overlap = compute_skill_overlap(candidate_skills, preferred)
    return float(overlap["normalized_overlap_score"])

# Override the basic string intersections with the new skill graph overlap metrics
fe.compute_retrieval_skill_score = skill_graph_retrieval_score
fe.compute_preferred_skill_score = skill_graph_preferred_score
logger.info("Skill Graph successfully bound to Feature Engineering scoring heuristics.")

# ==============================================================================
# MAIN RUNNER ORCHESTRATION PIPELINE
# ==============================================================================
def run_pipeline(
    candidates_path: str,
    jd_path: str,
    config_path: str
) -> Tuple[List[Dict], Dict[str, Any]]:
    """Runs the complete candidate discovery and ranking pipeline.

    Flow:
        1. Load Configurations and JD
        2. Stream Ingestion & Stage 1 Hard Exclusions (Honeypot + Service Firms)
        3. Stage 1 BM25 Sparse Index Retrieval (Top 2000)
        4. Stage 2 Dense Semantic Reranking (Top 500)
        5. Stage 3 Contextual Cross-Encoder Reranking (Top 150)
        6. Behavioral Scoring Fusion
        7. Recruiter Explainability Reasoning Generation
        8. Monotonic Ranks Assignment

    Args:
        candidates_path (str): Filepath of the pool candidate jsonl(.gz) database.
        jd_path (str): Filepath of the target role job description.
        config_path (str): Filepath of the ranking weights YAML configuration.

    Returns:
        Tuple[List[Dict], Dict[str, Any]]: The ranked candidate records and statistical metadata.
    """
    logger.info("Initializing Redrob Intelligent Ranking Pipeline...")
    
    # 1. Load Configurations and Job Description
    config: AppConfig = load_config(config_path)
    jd_text: str = load_job_description(jd_path)
    jd_spec: Dict = extract_requirements(jd_text)
    
    current_date = config.pipeline.current_date
    logger.info("Configurations loaded. Reference date: %s", current_date)

    # Extract hard-filter parameters from JD spec (fallback to configs if empty)
    exp_range = jd_spec.get("experience_range", {}) or {}
    min_exp = exp_range.get("min_years", config.retrieval.min_experience_years)
    max_exp = exp_range.get("max_years", config.retrieval.max_experience_years)
    if min_exp is None: min_exp = 3.0
    if max_exp is None: max_exp = 12.0

    # 2. Ingest Candidates and Apply Stage 1 Hard Filters
    logger.info("Ingesting candidate streams and parsing hard filters...")
    
    total_count = 0
    honeypots_count = 0
    consulting_count = 0
    role_filtered_count = 0
    exp_filtered_count = 0
    skill_filtered_count = 0
    filtered_candidates = []

    for cand in stream_candidates(candidates_path):
        total_count += 1
        cand_id = cand.get("candidate_id", "UNKNOWN")
        
        # Guard against malformed records
        if not isinstance(cand, dict):
            continue

        # A. Honeypot check
        if is_honeypot(cand, current_date):
            honeypots_count += 1
            logger.debug("Filtered Candidate %s: Triggered Honeypot flag.", cand_id)
            continue

        # B. Consulting company check
        if is_consulting_only(cand):
            consulting_count += 1
            logger.debug("Filtered Candidate %s: Consulting-only career history.", cand_id)
            continue

        # B2. Technical role check
        if not is_technical_role(cand):
            role_filtered_count += 1
            logger.debug("Filtered Candidate %s: Non-technical role headline.", cand_id)
            continue

        # C. Total Experience Fit check
        profile = cand.get("profile", {}) or {}
        y_exp = profile.get("years_of_experience")
        if y_exp is None:
            exp_filtered_count += 1
            continue
        try:
            y_exp_val = float(y_exp)
        except (ValueError, TypeError):
            exp_filtered_count += 1
            continue

        if y_exp_val < min_exp or y_exp_val > max_exp:
            exp_filtered_count += 1
            logger.debug("Filtered Candidate %s: Experience %.1f outside bounds.", cand_id, y_exp_val)
            continue

        # D. Must-have skill overlap check
        cand_skills = extract_candidate_skills(cand)
        must_have = jd_spec.get("must_have", [])
        must_have_overlap = compute_skill_overlap(cand_skills, must_have)
        if must_have_overlap.get("normalized_overlap_score", 0.0) == 0.0:
            skill_filtered_count += 1
            logger.debug("Filtered Candidate %s: 0 core skills match.", cand_id)
            continue

        filtered_candidates.append(cand)

    logger.info(
        "Candidate stream filtered. Clean records remaining: %d/%d (Removed: %d honeypots, %d consulting, %d non-tech role, %d exp mismatch, %d skill mismatch).",
        len(filtered_candidates),
        total_count,
        honeypots_count,
        consulting_count,
        role_filtered_count,
        exp_filtered_count,
        skill_filtered_count
    )

    if not filtered_candidates:
        logger.error("No candidates remaining after hard exclusions. Terminating pipeline.")
        return [], {
            "total_candidates": total_count,
            "honeypots_removed": honeypots_count,
            "consulting_only_removed": consulting_count,
            "experience_filtered": exp_filtered_count,
            "retrieval_count": 0,
            "semantic_count": 0,
            "cross_encoder_count": 0,
            "final_count": 0
        }

    # 3. Stage 1: BM25 Sparse Index Retrieval (up to stage1_top_k)
    logger.info("Executing Stage 1 Sparse Retrieval...")
    stage1_candidates, stage1_meta = retrieve_top_candidates(
        query=jd_text,
        candidates=filtered_candidates,
        top_k=config.retrieval.stage1_top_k,
        config=config,
        jd_spec=jd_spec
    )
    logger.info("Stage 1 retrieval completed. Candidates retrieved: %d", len(stage1_candidates))

    # 4. Stage 2: Dense Semantic Reranking (up to stage2_top_k)
    logger.info("Executing Stage 2 Dense Semantic Reranking...")
    stage2_candidates, stage2_meta = semantic_rerank(
        candidates=stage1_candidates,
        jd_text=jd_text,
        top_k=config.retrieval.stage2_top_k,
        config=config
    )
    logger.info("Stage 2 rerank completed. Candidates reranked: %d", len(stage2_candidates))

    # 5. Stage 3: Contextual Cross-Encoder Reranking (Top 150)
    logger.info("Executing Stage 3 Contextual Cross-Encoder Reranking...")
    # Reranks only the top 150 candidates to respect the CPU execution limits
    stage3_candidates, stage3_meta = cross_encoder_rerank(
        candidates=stage2_candidates,
        jd_text=jd_text,
        top_k=150,
        config=config
    )
    logger.info("Stage 3 rerank completed. Candidates processed: %d", len(stage3_candidates))

    # 6. Hybrid Score Fusion (Blending Cross-Encoder scores into Semantic Metadata)
    logger.info("Blending Cross-Encoder relevance scores into final scoring vectors...")
    ce_scores = {}
    for cand in stage3_candidates:
        ce_score = cand.get("cross_encoder_score", -1.0)
        cand_id = cand.get("candidate_id")
        if ce_score != -1.0 and cand_id is not None:
            ce_scores[cand_id] = ce_score

    # Normalize and blend Cross-Encoder scores into semantic_metadata scores
    if ce_scores:
        min_ce = min(ce_scores.values())
        max_ce = max(ce_scores.values())
        ce_range = max_ce - min_ce

        for cand_id, raw_ce in ce_scores.items():
            if ce_range > 1e-9:
                normed_ce = (raw_ce - min_ce) / ce_range
            else:
                normed_ce = 1.0
            
            orig_sem = stage2_meta["scores"].get(cand_id, 0.0)
            normed_sem = (orig_sem + 1.0) / 2.0  # Shift bi-encoder CosSim [-1, 1] -> [0, 1]
            
            # Weighted hybrid semantic blend: 70% Cross-Encoder, 30% Bi-Encoder
            blended_sem = 0.7 * normed_ce + 0.3 * normed_sem
            
            # Map back to expected [-1, 1] range for final fuse_scores
            stage2_meta["scores"][cand_id] = blended_sem * 2.0 - 1.0

    # 7. Fuse final scores and rank candidates (combining signals, exp, location, company type)
    logger.info("Executing final scoring fusion and behavioral ranking...")
    ranked_candidates, final_meta = final_rank(
        candidates=stage3_candidates,
        retrieval_metadata=stage1_meta,
        semantic_metadata=stage2_meta,
        jd_spec=jd_spec,
        config=config
    )

    # 8. Recruiter Explanation and Reasoning Generation for Shortlist (Top 100)
    logger.info("Generating explanation reasonings for the ranked shortlist...")
    final_shortlist = ranked_candidates[:config.retrieval.final_top_k]
    
    for cand in final_shortlist:
        score = cand.get("fused_score", 0.0)
        rank = cand.get("rank", 1)
        reasoning = generate_candidate_reasoning(cand, score, rank, jd_spec)
        cand["reasoning"] = reasoning

    # Assemble stats for execution logging and CLI outputs
    report_data = {
        "total_candidates": total_count,
        "honeypots_removed": honeypots_count,
        "consulting_only_removed": consulting_count,
        "role_filtered": role_filtered_count,
        "experience_filtered": exp_filtered_count,
        "retrieval_count": len(stage1_candidates),
        "semantic_count": len(stage2_candidates),
        "cross_encoder_count": len(ce_scores),
        "final_count": len(final_shortlist)
    }

    return final_shortlist, report_data


# ==============================================================================
# SUBMISSION PERSISTENCE LAYER
# ==============================================================================
def save_submission(ranked_candidates: List[Dict], output_path: str) -> None:
    """Saves the top 100 ranked candidates to a CSV file matching the hackathon schema.

    Schema:
        candidate_id,rank,score,reasoning

    Args:
        ranked_candidates (List[Dict]): Final scored shortlist of candidate records.
        output_path (str): Target filepath destination for output CSV.
    """
    logger.info("Writing submission CSV to '%s'...", output_path)
    
    # Ensure nested directory tree exists
    dir_name = os.path.dirname(output_path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)
        
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["candidate_id", "rank", "score", "reasoning"])
            
            for cand in ranked_candidates:
                cid = cand.get("candidate_id")
                rank = cand.get("rank")
                score = cand.get("fused_score", 0.0)
                reasoning = cand.get("reasoning", "")
                
                # Format candidate_id safely to always output CAND_XXXXXXX
                if isinstance(cid, int):
                    cid = f"CAND_{cid:07d}"
                else:
                    cid = str(cid).strip()

                writer.writerow([cid, rank, f"{score:.6f}", reasoning])
                
        logger.info("Submission successfully written. Count: %d rows.", len(ranked_candidates))
    except Exception as e:
        logger.exception("Failed to write submission CSV: %s", str(e))
        raise


# ==============================================================================
# PIPELINE REPORT GENERATOR
# ==============================================================================
def generate_pipeline_report(report_data: Dict[str, Any], runtime: float) -> str:
    """Formats overall pipeline execution statistics into a clean text report.

    Args:
        report_data (Dict[str, Any]): Cumulative statistics dict.
        runtime (float): Elapsed wall-clock time in seconds.

    Returns:
        str: Styled summary report text.
    """
    total = report_data.get("total_candidates", 0)
    removed_honeypots = report_data.get("honeypots_removed", 0)
    removed_consulting = report_data.get("consulting_only_removed", 0)
    removed_role = report_data.get("role_filtered", 0)
    removed_exp = report_data.get("experience_filtered", 0)
    valid_stage1 = total - removed_honeypots - removed_consulting - removed_role - removed_exp

    report = f"""
================================================================================
                    REDROB PIPELINE EXECUTION REPORT                            
================================================================================
Total Candidate Profiles Streamed:      {total:,}
Honeypot Trap Anomalies Discarded:      {removed_honeypots:,}
Consulting-Only Careers Discarded:      {removed_consulting:,}
Non-Technical Roles Discarded:          {removed_role:,}
Stated Experience Outside Range:        {removed_exp:,}
Valid Stage 1 Sparse Input Size:        {valid_stage1:,}

Stage 1 Sparse Retrieval Count (BM25):  {report_data.get('retrieval_count'):,}
Stage 2 Dense Reranking Count (Bi):    {report_data.get('semantic_count'):,}
Stage 3 Contextual Reranking (Cross):   {report_data.get('cross_encoder_count'):,}
Final Ranked Shortlist Exported:        {report_data.get('final_count'):,}

Total Pipeline Runtime:                 {runtime:.2f} seconds
================================================================================
"""
    return report


# ==============================================================================
# COMMAND LINE ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Redrob Intelligent Candidate Discovery & Ranking Pipeline CLI"
    )
    parser.add_argument(
        "--candidates",
        type=str,
        default="data/raw/candidates.jsonl",
        help="Path to candidates.jsonl file (supports .jsonl or .gz)."
    )
    parser.add_argument(
        "--out",
        type=str,
        default="data/processed/submission.csv",
        help="Path to write the output ranked CSV."
    )
    parser.add_argument(
        "--config",
        type=str,
        default="configs/ranking_config.yaml",
        help="Path to the ranking configuration file."
    )
    parser.add_argument(
        "--jd",
        type=str,
        default="data/raw/job_description.txt",
        help="Path to the job description text file."
    )

    args = parser.parse_args()

    start_time = time.time()
    try:
        # Run end-to-end orchestration
        shortlist, stats = run_pipeline(
            candidates_path=args.candidates,
            jd_path=args.jd,
            config_path=args.config
        )
        
        # Save submission CSV
        save_submission(shortlist, args.out)
        
        # Print metrics report
        end_time = time.time()
        elapsed = end_time - start_time
        report = generate_pipeline_report(stats, elapsed)
        
        # Print report and save log
        print(report)
        logger.info("Pipeline executed successfully in %.2f seconds.", elapsed)
        
    except Exception as e:
        logger.exception("Pipeline execution failed with fatal error: %s", str(e))
        sys.exit(1)
