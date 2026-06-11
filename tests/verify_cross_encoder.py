import sys
import os

# Ensure correct path resolution
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.cross_encoder_reranker import (
    load_cross_encoder,
    build_candidate_text,
    score_candidate_pairs,
    rerank_candidates,
)
from src.config import load_config


def run_tests():
    print("Starting CrossEncoder Reranker Verification...")

    # 1. Test build_candidate_text
    candidate = {
        "candidate_id": "CAND_999",
        "profile": {
            "headline": "Lead Search Architect",
            "summary": "Building dense retrieval platforms",
            "current_title": "Senior Staff Engineer",
        },
        "skills": ["faiss", "pinecone", "python"],
        "career_history": [
            {"title": "MLE", "company": "ProductCorp", "description": "Built vector indexes"}
        ]
    }
    candidate_text = build_candidate_text(candidate)
    print(f"  -> build_candidate_text output: '{candidate_text}'")
    assert "lead search architect" in candidate_text
    assert "faiss" in candidate_text
    assert "productcorp" in candidate_text
    print("  -> build_candidate_text: PASSED")

    # 2. Test rerank_candidates (with fallback verification)
    candidates = [
        {
            "candidate_id": "CAND_001",
            "profile": {
                "headline": "Marketing Professional",
                "summary": "Experienced in social media campaigns",
                "current_title": "Marketing Lead"
            },
            "skills": ["marketing", "SEO"],
            "career_history": []
        },
        {
            "candidate_id": "CAND_002",
            "profile": {
                "headline": "Senior AI Systems Engineer",
                "summary": "Designed embeddings and vector search platforms",
                "current_title": "Founding AI Engineer"
            },
            "skills": ["embeddings", "vector search", "faiss", "python"],
            "career_history": [
                {"title": "AI Engineer", "company": "Foundry", "description": "Implemented cross-encoder rerankers"}
            ]
        }
    ]

    jd_text = "Looking for a Founding AI Engineer with experience in vector search, embeddings, and cross-encoder models"

    # Try loading real model or falling back
    config = load_config("configs/ranking_config.yaml")
    
    # We will run the reranking
    ranked, metadata = rerank_candidates(candidates, jd_text, top_k=10, config=config)

    assert len(ranked) == 2, "Should return all candidates"
    assert "cross_encoder_score" in ranked[0], "Should have cross_encoder_score metadata"
    assert "rank" in ranked[0], "Should have rank metadata"

    # CAND_002 should rank first because its overlap or semantic score is much higher
    assert ranked[0]["candidate_id"] == "CAND_002", f"Expected CAND_002 to be ranked first, got {ranked[0]['candidate_id']}"
    assert ranked[0]["rank"] == 1
    assert ranked[1]["rank"] == 2

    # Verify metadata structure
    assert "scores" in metadata
    assert "CAND_002" in metadata["scores"]
    assert "cross_encoder_score" in metadata["scores"]["CAND_002"]
    assert "rank" in metadata["scores"]["CAND_002"]

    print("  -> rerank_candidates execution and fallback checks: PASSED")
    print("CrossEncoder Reranker Verification: ALL TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    run_tests()
