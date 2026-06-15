import { Candidate, candidatesData } from "./data";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface CandidateAPI {
  candidate_id: string;
  rank: number;
  score: number;
  reasoning: string;
}

export interface StatsAPI {
  total_ingested: number;
  honeypots_removed: number;
  consulting_removed: number;
  valid_pool: number;
  bm25_top_k: number;
  biencoder_top_k: number;
  crossencoder_top_k: number;
  final_shortlist: number;
  runtime_seconds: number;
  peak_memory_mb: number;
  ndcg_at_10: number;
  llm_judge_ndcg: number;
  llm_judge_precision: number;
}

// Helper to dynamically parse and enrich API records
export function enrichCandidate(cand: CandidateAPI): Candidate {
  // If the candidate exists in our local dataset, inherit high-fidelity details
  const local = candidatesData.find(c => c.candidate_id === cand.candidate_id);
  if (local) {
    return {
      ...local,
      rank: cand.rank,
      score: cand.score,
      reasoning: cand.reasoning
    };
  }
  
  const text = cand.reasoning || "";
  
  // Extract skills
  let skills: string[] = [];
  const skillsMatch = text.match(/matching \d+ core skills \(([^)]+)\)/i);
  if (skillsMatch && skillsMatch[1]) {
    skills = skillsMatch[1].split(",").map((s) => s.trim().replace(/^and\s+/, ""));
  } else {
    skills = ["Python", "AI Engineering"];
  }
  
  // Extract notice period
  let notice_period = 30;
  const noticeMatch = text.match(/(\d+)-day notice period/i);
  if (noticeMatch && noticeMatch[1]) {
    notice_period = parseInt(noticeMatch[1], 10);
  }
  
  // Extract experience
  let experience = 5.0;
  const expMatch = text.match(/with (\d+(\.\d+)?) years/i);
  if (expMatch && expMatch[1]) {
    experience = parseFloat(expMatch[1]);
  }
  
  // Extract headline
  let headline = "AI Specialist";
  const headlineMatch = text.match(/^([a-zA-Z\s()-]+?) with/i);
  if (headlineMatch && headlineMatch[1]) {
    headline = headlineMatch[1].trim();
  }
  
  // Extract location
  let location = "Noida";
  const locMatch = text.match(/([a-zA-Z\s]+) location/i);
  if (locMatch && locMatch[1]) {
    location = locMatch[1].trim();
  } else if (text.toLowerCase().includes("bangalore")) {
    location = "Bangalore";
  } else if (text.toLowerCase().includes("pune")) {
    location = "Pune";
  }
  
  // Extract response rate
  let response_rate = 70;
  const respMatch = text.match(/(\d+)% recruiter response/i);
  if (respMatch && respMatch[1]) {
    response_rate = parseInt(respMatch[1], 10);
  }
  
  return {
    candidate_id: cand.candidate_id,
    rank: cand.rank,
    score: cand.score,
    reasoning: cand.reasoning,
    skills,
    notice_period,
    semantic_score: Math.min(98, Math.max(60, Math.floor(cand.score * 85))),
    skill_score: Math.min(100, Math.max(50, skills.length * 15 + 30)),
    behavioral_score: Math.min(100, Math.max(40, 100 - notice_period)),
    experience,
    headline,
    location,
    response_rate
  };
}

export async function fetchCandidates(): Promise<CandidateAPI[]> {
  try {
    const res = await fetch(`${API_BASE}/api/candidates`);
    if (!res.ok) throw new Error("API failed");
    return await res.json();
  } catch {
    // Fallback to local data if API is offline
    return candidatesData.map(c => ({
      candidate_id: c.candidate_id,
      rank: c.rank,
      score: c.score,
      reasoning: c.reasoning
    }));
  }
}

export async function fetchStats(): Promise<StatsAPI> {
  try {
    const res = await fetch(`${API_BASE}/api/stats`);
    if (!res.ok) throw new Error("API failed");
    return await res.json();
  } catch {
    // Fallback stats
    return {
      total_ingested: 100000,
      honeypots_removed: 65,
      consulting_removed: 7026,
      valid_pool: 14217,
      bm25_top_k: 2000,
      biencoder_top_k: 500,
      crossencoder_top_k: 150,
      final_shortlist: 100,
      runtime_seconds: 167.45,
      peak_memory_mb: 128.4,
      ndcg_at_10: 1.0,
      llm_judge_ndcg: 0.8708,
      llm_judge_precision: 1.0
    };
  }
}
