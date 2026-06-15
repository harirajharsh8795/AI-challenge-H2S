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
    candidate_id: "CAND_0068351",
    rank: 1,
    score: 1.111792,
    reasoning: "Lead AI Engineer with 6.4 years of experience, matching 4 core skills (Lora, Peft, Python, Qdrant) and showing a strong product company history. They are open to work (active within 90 days) with a 0-day notice period and 86% recruiter response rate.",
    skills: ['Lora', 'Peft', 'Python', 'Qdrant'],
    notice_period: 0,
    semantic_score: 95,
    skill_score: 90,
    behavioral_score: 86,
    experience: 6.4,
    headline: "Lead AI Engineer",
    location: "Delhi NCR",
    response_rate: 86
  },
  {
    candidate_id: "CAND_0080766",
    rank: 2,
    score: 1.037912,
    reasoning: "Staff Machine Learning Engineer with 8.8 years of experience, matching 3 core skills (Lora, Python, Qlora) and showing a strong product company history. They are open to work (active within 90 days) with a 0-day notice period and 66% recruiter response rate.",
    skills: ['Lora', 'Python', 'Qlora'],
    notice_period: 0,
    semantic_score: 88,
    skill_score: 85,
    behavioral_score: 66,
    experience: 8.8,
    headline: "Staff Machine Learning Engineer",
    location: "Coimbatore",
    response_rate: 66
  },
  {
    candidate_id: "CAND_0088025",
    rank: 3,
    score: 1.013153,
    reasoning: "Staff Machine Learning Engineer with 8.6 years of experience, matching 5 core skills (Lora, Pinecone, Python, Qlora, Rag) and showing a strong product company history. They are open to work (active within 90 days) with a 90-day notice period and 83% recruiter response rate.",
    skills: ['Lora', 'Pinecone', 'Python', 'Qlora', 'Rag'],
    notice_period: 90,
    semantic_score: 86,
    skill_score: 92,
    behavioral_score: 83,
    experience: 8.6,
    headline: "Staff Machine Learning Engineer",
    location: "Jaipur",
    response_rate: 83
  },
  {
    candidate_id: "CAND_0046525",
    rank: 4,
    score: 1.005239,
    reasoning: "Senior Machine Learning Engineer with 6.1 years of experience, matching 2 core skills (Langchain, Qdrant) and showing a strong product company history. They are open to work (active within 30 days) with a 60-day notice period and 88% recruiter response rate.",
    skills: ['Langchain', 'Qdrant'],
    notice_period: 60,
    semantic_score: 85,
    skill_score: 80,
    behavioral_score: 88,
    experience: 6.1,
    headline: "Senior Machine Learning Engineer",
    location: "Pune",
    response_rate: 88
  },
  {
    candidate_id: "CAND_0046064",
    rank: 5,
    score: 0.999305,
    reasoning: "Senior NLP Engineer with 8.9 years of experience, matching 4 core skills (Peft, Pinecone, Python, Qlora) and showing a strong product company history. They are open to work (active within 90 days) with a 30-day notice period and 78% recruiter response rate.",
    skills: ['Peft', 'Pinecone', 'Python', 'Qlora'],
    notice_period: 30,
    semantic_score: 84,
    skill_score: 85,
    behavioral_score: 78,
    experience: 8.9,
    headline: "Senior NLP Engineer",
    location: "Coimbatore",
    response_rate: 78
  },
  {
    candidate_id: "CAND_0050454",
    rank: 6,
    score: 0.993666,
    reasoning: "AI Engineer with 6.8 years of experience, matching 5 core skills (Faiss, Langchain, Lora, Qdrant, Qlora) and showing a strong product company history. They are open to work (active within 90 days) with a 30-day notice period and 77% recruiter response rate.",
    skills: ['Faiss', 'Langchain', 'Lora', 'Qdrant', 'Qlora'],
    notice_period: 30,
    semantic_score: 84,
    skill_score: 92,
    behavioral_score: 77,
    experience: 6.8,
    headline: "AI Engineer",
    location: "Delhi NCR",
    response_rate: 77
  },
  {
    candidate_id: "CAND_0071974",
    rank: 7,
    score: 0.988268,
    reasoning: "Senior AI Engineer with 7.8 years of experience, matching 6 core skills (Embeddings, Lora, Peft, Pinecone, Qdrant, and 1 more) and showing a strong product company history. They are open to work (active within 90 days) with a 45-day notice period and 76% recruiter response rate.",
    skills: ['Embeddings', 'LoRA', 'PEFT', 'Pinecone', 'Qdrant', 'Sentence Transformers'],
    notice_period: 45,
    semantic_score: 83,
    skill_score: 94,
    behavioral_score: 76,
    experience: 7.8,
    headline: "Senior AI Engineer",
    location: "Vizag",
    response_rate: 76
  },
  {
    candidate_id: "CAND_0077337",
    rank: 8,
    score: 0.982353,
    reasoning: "Staff Machine Learning Engineer with 7.0 years of experience, matching 5 core skills (Pinecone, Python, Qdrant, Qlora, Rag) and showing a strong product company history. They are open to work (active within 30 days) with a 60-day notice period and 95% recruiter response rate.",
    skills: ['Pinecone', 'Python', 'Qdrant', 'Qlora', 'Rag'],
    notice_period: 60,
    semantic_score: 83,
    skill_score: 92,
    behavioral_score: 95,
    experience: 7.0,
    headline: "Staff Machine Learning Engineer",
    location: "Kochi",
    response_rate: 95
  },
  {
    candidate_id: "CAND_0079064",
    rank: 9,
    score: 0.959483,
    reasoning: "Senior Data Scientist with 5.2 years of experience, matching 2 core skills (Pinecone, Qlora) and showing a strong product company history. They are open to work (active within 90 days) with a 120-day notice period and 91% recruiter response rate.",
    skills: ['Pinecone', 'Qlora'],
    notice_period: 120,
    semantic_score: 81,
    skill_score: 75,
    behavioral_score: 91,
    experience: 5.2,
    headline: "Senior Data Scientist",
    location: "Noida",
    response_rate: 91
  },
  {
    candidate_id: "CAND_0009024",
    rank: 10,
    score: 0.95756,
    reasoning: "Search Engineer with 5.2 years of experience, matching 4 core skills (Faiss, Lora, Peft, Qdrant) and showing a strong product company history. They are open to work (active within 90 days) with a 30-day notice period and 46% recruiter response rate.",
    skills: ['Faiss', 'Lora', 'Peft', 'Qdrant'],
    notice_period: 30,
    semantic_score: 81,
    skill_score: 85,
    behavioral_score: 46,
    experience: 5.2,
    headline: "Search Engineer",
    location: "Chennai",
    response_rate: 46
  }
];
