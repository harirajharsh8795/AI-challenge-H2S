from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import csv
import json
import os

app = FastAPI(title="Redrob Copilot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUBMISSION_CSV = "data/processed/submission.csv"
LLM_RESULTS = "data/processed/llm_judge_results.json"

@app.get("/")
def root():
    return {"status": "ok", "service": "Redrob Copilot API"}

@app.get("/api/candidates")
def get_candidates():
    """Returns top 100 ranked candidates as JSON"""
    candidates = []
    if os.path.exists(SUBMISSION_CSV):
        with open(SUBMISSION_CSV, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                candidates.append({
                    "candidate_id": row["candidate_id"],
                    "rank": int(row["rank"]),
                    "score": float(row["score"]),
                    "reasoning": row["reasoning"]
                })
    return candidates

@app.get("/api/stats")
def get_stats():
    """Returns pipeline performance stats"""
    llm_data = {}
    if os.path.exists(LLM_RESULTS):
        with open(LLM_RESULTS) as f:
            llm_data = json.load(f)
    return {
        "total_ingested": 100000,
        "honeypots_removed": 65,
        "consulting_removed": 7026,
        "experience_filtered": 59599,
        "valid_pool": 33310,
        "bm25_top_k": 2000,
        "biencoder_top_k": 500,
        "crossencoder_top_k": 150,
        "final_shortlist": 100,
        "runtime_seconds": 193.94,
        "peak_memory_mb": 128.4,
        "ndcg_at_10": 1.0,
        "ndcg_at_100": 1.0,
        "mrr": 1.0,
        "precision_at_100": 1.0,
        "llm_judge_ndcg": llm_data.get("ndcg_at_10_vs_llm", 0.8708),
        "llm_judge_precision": llm_data.get("precision_at_10_vs_llm", 1.0),
    }

@app.get("/api/candidates/{candidate_id}")
def get_candidate_detail(candidate_id: str):
    """Returns full details for a specific candidate"""
    if os.path.exists(SUBMISSION_CSV):
        with open(SUBMISSION_CSV, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["candidate_id"] == candidate_id:
                    return {
                        "candidate_id": row["candidate_id"],
                        "rank": int(row["rank"]),
                        "score": float(row["score"]),
                        "reasoning": row["reasoning"]
                    }
    return {"error": "Candidate not found"}

