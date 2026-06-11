import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import os
from src.jd_parser import extract_skills, extract_experience_requirements, extract_location_preferences, build_skill_clusters, extract_requirements

def run_test():
    print("Initializing JDParser verification...")

    # 1. Test extract_skills
    sample_text = "We require experience with embeddings, vector search, Pinecone, and PEFT. Strong Python is needed."
    skills = extract_skills(sample_text)
    print(f"Extracted skills: {skills}")
    expected_skills = {"embeddings", "vector search", "pinecone", "peft", "python"}
    assert set(skills) == expected_skills, f"extract_skills failed: got {skills}"
    print("extract_skills: SUCCESS")

    # 2. Test extract_experience_requirements
    exp1 = extract_experience_requirements("Candidate must have 5-9 years of experience in ML.")
    print(f"Parsed exp1 (5-9): {exp1}")
    assert exp1["min_years"] == 5.0 and exp1["max_years"] == 9.0

    exp2 = extract_experience_requirements("We require 6 to 8 years experience.")
    print(f"Parsed exp2 (6 to 8): {exp2}")
    assert exp2["min_years"] == 6.0 and exp2["max_years"] == 8.0

    exp3 = extract_experience_requirements("Minimum 4+ years of Python.")
    print(f"Parsed exp3 (4+): {exp3}")
    assert exp3["min_years"] == 4.0 and exp3["max_years"] is None
    print("extract_experience_requirements: SUCCESS")

    # 3. Test extract_location_preferences
    loc_text = "We have offices in Noida and Pune. Candidates from Hyderabad are also welcome."
    locs = extract_location_preferences(loc_text)
    print(f"Extracted locations: {locs}")
    assert set(locs) == {"Noida", "Pune", "Hyderabad"}, f"extract_location_preferences failed: got {locs}"
    print("extract_location_preferences: SUCCESS")

    # 4. Test build_skill_clusters
    clusters = build_skill_clusters()
    print(f"Predefined clusters: {list(clusters.keys())}")
    assert "retrieval" in clusters and "evaluation" in clusters and "llm" in clusters and "systems" in clusters
    print("build_skill_clusters: SUCCESS")

    # 5. Test extract_requirements with mock JD content
    mock_jd = """
    Job Description: AI Engineer
    Location: Pune/Noida, India (Hybrid)
    Experience Required: 5-9 years

    Things you absolutely need:
    * Production experience with embeddings-based retrieval systems.
    * Strong Python.
    * Evaluation frameworks (NDCG, MAP).

    Things we'd like you to have:
    * LLM fine-tuning experience (LoRA, PEFT).

    Things we explicitly do NOT want:
    * Consulting-only candidates (TCS, Infosys).
    * LangChain-only developers.
    """
    
    spec = extract_requirements(mock_jd)
    print("Parsed Spec must_have:", spec["must_have"])
    print("Parsed Spec preferred:", spec["preferred"])
    print("Parsed Spec excluded:", spec["excluded"])
    print("Parsed Spec locations:", spec["locations"])
    print("Parsed Spec exp:", spec["experience_range"])
    
    assert "embeddings" in spec["must_have"]
    assert "lora" in spec["preferred"]
    assert "consulting-only candidates" in spec["excluded"]
    assert "Noida" in spec["locations"] and "Pune" in spec["locations"]
    assert spec["experience_range"]["min_years"] == 5.0
    
    # 6. Test with actual JD file if available
    jd_file = "job_description.txt"
    if os.path.exists(jd_file):
        with open(jd_file, "r", encoding="utf-8") as f:
            real_jd = f.read()
        real_spec = extract_requirements(real_jd)
        print(f"Real JD Locations: {real_spec['locations']}")
        print(f"Real JD Experience: {real_spec['experience_range']}")
    
    print("extract_requirements: SUCCESS")
    print("ALL TESTS COMPLETED SUCCESSFULLY!")

if __name__ == '__main__':
    run_test()
