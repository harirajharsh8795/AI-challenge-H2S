import sys
import os
from typing import Set

# Ensure correct path resolution
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.skill_graph import (
    build_skill_graph,
    get_global_graph,
    expand_skill,
    expand_skill_set,
    compute_skill_overlap,
)


def run_tests():
    print("Starting SkillGraph Verification...")

    # 1. Test build_skill_graph and get_global_graph
    graph = get_global_graph()
    assert isinstance(graph, dict), "Graph must be a dictionary"
    assert "embeddings" in graph, "'embeddings' must be a node in the graph"
    assert "dense retrieval" in graph["embeddings"], "'embeddings' must connect to 'dense retrieval'"
    assert "embeddings" in graph["dense retrieval"], "'dense retrieval' must connect to 'embeddings'"
    print("  -> graph construction checks: PASSED")

    # 2. Test expand_skill for a known chain
    # embeddings ↔ dense retrieval ↔ semantic search ↔ vector search
    expanded_embeddings = expand_skill("embeddings")
    expected_chain = {"embeddings", "dense retrieval", "semantic search", "vector search"}
    assert expanded_embeddings == expected_chain, f"Expected {expected_chain}, got {expanded_embeddings}"

    # Test case insensitivity and whitespace trimming
    expanded_mixed = expand_skill("  Embeddings  ")
    assert expanded_mixed == expected_chain, f"Expected case-insensitive trim expansion to match: {expanded_mixed}"

    # Test unknown skill
    expanded_unknown = expand_skill("unknown_skill")
    assert expanded_unknown == {"unknown_skill"}, f"Expected self-expansion, got {expanded_unknown}"
    print("  -> expand_skill checks: PASSED")

    # 3. Test expand_skill_set
    skills = ["embeddings", "faiss"]
    expanded_set = expand_skill_set(skills)
    assert "vector search" in expanded_set, "Should expand embeddings to vector search"
    assert "vector indexing" in expanded_set, "Should expand faiss to vector indexing"
    print("  -> expand_skill_set checks: PASSED")

    # 4. Test compute_skill_overlap (Retrieval Engineer Thinking)
    candidate_skills = ["embeddings", "faiss", "python"]
    jd_skills = ["dense retrieval", "vector indexing", "python", "docker"]

    overlap_results = compute_skill_overlap(candidate_skills, jd_skills)

    # Output structure validation
    assert "overlap_score" in overlap_results
    assert "normalized_overlap_score" in overlap_results
    assert "direct_matches" in overlap_results
    assert "semantic_matches" in overlap_results
    assert "unmatched_skills" in overlap_results
    assert "match_details" in overlap_results

    # "python" is a direct match
    assert "python" in overlap_results["direct_matches"]
    assert overlap_results["match_details"]["python"]["distance"] == 0
    assert overlap_results["match_details"]["python"]["score"] == 1.0

    # "dense retrieval" should match candidate "embeddings" (1 hop away: embeddings ↔ dense retrieval)
    assert "dense retrieval" in overlap_results["semantic_matches"]
    assert overlap_results["match_details"]["dense retrieval"]["distance"] == 1
    assert abs(overlap_results["match_details"]["dense retrieval"]["score"] - 0.8) < 1e-9

    # "vector indexing" should match candidate "faiss" (2 hops away: faiss ↔ vector database ↔ vector indexing)
    assert "vector indexing" in overlap_results["semantic_matches"]
    assert overlap_results["match_details"]["vector indexing"]["distance"] == 2
    assert abs(overlap_results["match_details"]["vector indexing"]["score"] - 0.64) < 1e-9

    # "docker" is unmatched
    assert "docker" in overlap_results["unmatched_skills"]
    assert overlap_results["match_details"]["docker"]["distance"] == -1
    assert overlap_results["match_details"]["docker"]["score"] == 0.0

    # Overall Scores
    # Expected: 1.0 (python) + 0.8 (dense retrieval) + 0.64 (vector indexing) + 0.0 (docker) = 2.44
    # Normalized: 2.44 / 4 = 0.61
    expected_score = 1.0 + 0.8 + 0.64 + 0.0
    assert abs(overlap_results["overlap_score"] - expected_score) < 1e-9, f"Expected {expected_score}, got {overlap_results['overlap_score']}"
    assert abs(overlap_results["normalized_overlap_score"] - (expected_score / 4.0)) < 1e-9
    
    print("  -> compute_skill_overlap checks: PASSED")
    print("SkillGraph Verification: ALL TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    run_tests()
