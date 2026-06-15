export interface Candidate {
  candidate_id: string;
  rank: number;
  score: number;
  reasoning: string;
  skills: string[];
  notice_period: number; // 0, 30, 90
  semantic_score: number; // percentage (0-100)
  skill_score: number;    // percentage (0-100)
  behavioral_score: number; // percentage (0-100)
  experience: number;
  headline: string;
  location: string;
  response_rate: number; // percentage (0-100)
}

export const candidatesData: Candidate[] = [
  {
    candidate_id: "CAND_0080766",
    rank: 1,
    score: 1.054635,
    reasoning: "Staff Machine Learning Engineer with 8.8 years of experience, matching 3 core skills (Lora, Python, Qlora) and showing a strong product company history. They are open to work (active within 90 days) with a 0-day notice period and 66% recruiter response rate.",
    skills: ["Lora", "Python", "Qlora"],
    notice_period: 0,
    semantic_score: 95,
    skill_score: 85,
    behavioral_score: 75,
    experience: 8.8,
    headline: "Staff Machine Learning Engineer",
    location: "Noida",
    response_rate: 66
  },
  {
    candidate_id: "CAND_0068351",
    rank: 2,
    score: 1.033365,
    reasoning: "Lead AI Engineer with 6.4 years of experience, matching 4 core skills (Lora, Peft, Python, Qdrant) and showing a strong product company history. They are open to work (active within 90 days) with a 0-day notice period and 86% recruiter response rate.",
    skills: ["Lora", "Peft", "Python", "Qdrant"],
    notice_period: 0,
    semantic_score: 90,
    skill_score: 95,
    behavioral_score: 88,
    experience: 6.4,
    headline: "Lead AI Engineer",
    location: "Noida",
    response_rate: 86
  },
  {
    candidate_id: "CAND_0088025",
    rank: 3,
    score: 1.029999,
    reasoning: "Staff Machine Learning Engineer with 8.6 years of experience, matching 5 core skills (Bm25, Lora, Pinecone, Python, Qlora) and showing a strong product company history. They are open to work (active within 30 days) with a 90-day notice period and 83% recruiter response rate.",
    skills: ["Bm25", "Lora", "Pinecone", "Python", "Qlora"],
    notice_period: 90,
    semantic_score: 98,
    skill_score: 92,
    behavioral_score: 65,
    experience: 8.6,
    headline: "Staff Machine Learning Engineer",
    location: "Pune",
    response_rate: 83
  },
  {
    candidate_id: "CAND_0046064",
    rank: 4,
    score: 1.017068,
    reasoning: "Senior NLP Engineer with 8.9 years of experience, matching 5 core skills (Bm25, Peft, Pinecone, Python, Qlora) and showing a strong product company history. They are open to work (active within 90 days) with a 30-day notice period and 78% recruiter response rate.",
    skills: ["Bm25", "Peft", "Pinecone", "Python", "Qlora"],
    notice_period: 30,
    semantic_score: 91,
    skill_score: 89,
    behavioral_score: 72,
    experience: 8.9,
    headline: "Senior NLP Engineer",
    location: "Noida",
    response_rate: 78
  },
  {
    candidate_id: "CAND_0043676",
    rank: 5,
    score: 1.011916,
    reasoning: "Senior Software Engineer (ML) with 6.1 years of experience, matching 3 core skills (Lora, Peft, Qlora) and showing a strong product company history. They are open to work (inactive for 103 days) with a 30-day notice period and 65% recruiter response rate.",
    skills: ["Lora", "Peft", "Qlora"],
    notice_period: 30,
    semantic_score: 87,
    skill_score: 82,
    behavioral_score: 60,
    experience: 6.1,
    headline: "Senior Software Engineer (ML)",
    location: "Bangalore",
    response_rate: 65
  },
  {
    candidate_id: "CAND_0071974",
    rank: 6,
    score: 1.005957,
    reasoning: "Senior AI Engineer with 7.8 years of experience, matching 7 core skills (Bm25, Embeddings, Lora, Peft, Pinecone) and showing a strong product company history. They are open to work (active within 90 days) with a 30-day notice period and 76% recruiter response rate.",
    skills: ["Bm25", "Embeddings", "Lora", "Peft", "Pinecone"],
    notice_period: 30,
    semantic_score: 93,
    skill_score: 88,
    behavioral_score: 68,
    experience: 7.8,
    headline: "Senior AI Engineer",
    location: "Hyderabad",
    response_rate: 76
  },
  {
    candidate_id: "CAND_0028793",
    rank: 7,
    score: 1.000383,
    reasoning: "Search Engineer with 7.2 years of experience, matching 4 core skills (Embeddings, Lora, Peft, Qlora) and showing a strong product company history. They are open to work (active within 90 days) with a 90-day notice period and 56% recruiter response rate.",
    skills: ["Embeddings", "Lora", "Peft", "Qlora"],
    notice_period: 90,
    semantic_score: 86,
    skill_score: 84,
    behavioral_score: 52,
    experience: 7.2,
    headline: "Search Engineer",
    location: "Pune",
    response_rate: 56
  },
  {
    candidate_id: "CAND_0009024",
    rank: 8,
    score: 0.975488,
    reasoning: "Search Engineer with 5.2 years of experience, matching 4 core skills (Faiss, Lora, Peft, Qdrant) and showing a strong product company history. They are open to work (active within 90 days) with a 30-day notice period and 46% recruiter response rate.",
    skills: ["Faiss", "Lora", "Peft", "Qdrant"],
    notice_period: 30,
    semantic_score: 82,
    skill_score: 80,
    behavioral_score: 48,
    experience: 5.2,
    headline: "Search Engineer",
    location: "Noida",
    response_rate: 46
  },
  {
    candidate_id: "CAND_0079064",
    rank: 9,
    score: 0.968648,
    reasoning: "Senior Data Scientist with 5.2 years of experience, matching 2 core skills (Pinecone, Qlora) and showing a strong product company history. They are open to work (active within 90 days) with a 90-day notice period and 91% recruiter response rate.",
    skills: ["Pinecone", "Qlora"],
    notice_period: 90,
    semantic_score: 79,
    skill_score: 70,
    behavioral_score: 45,
    experience: 5.2,
    headline: "Senior Data Scientist",
    location: "Delhi NCR",
    response_rate: 91
  },
  {
    candidate_id: "CAND_0002025",
    rank: 10,
    score: 0.966371,
    reasoning: "Senior AI Engineer with 5.9 years of experience, matching 5 core skills (Faiss, Pinecone, Python, Qlora, Weaviate) and showing a strong product company history. They are open to work (active within 30 days) with a 30-day notice period and 80% recruiter response rate.",
    skills: ["Faiss", "Pinecone", "Python", "Qlora", "Weaviate"],
    notice_period: 30,
    semantic_score: 89,
    skill_score: 87,
    behavioral_score: 80,
    experience: 5.9,
    headline: "Senior AI Engineer",
    location: "Bangalore",
    response_rate: 80
  }
];
