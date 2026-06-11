export interface Candidate {
  candidate_id: string;
  rank: number;
  score: number;
  fused_score?: number;
  headline: string;
  years_of_experience: number;
  location: string;
  notice_period_days: number;
  recruiter_response_rate: number;
  last_active_days: number;
  github_activity_score: number;
  open_to_work_flag: boolean;
  company_background: "Product" | "Consulting" | "Mixed";
  must_have_skills: string[];
  preferred_skills: string[];
  expanded_skills: string[];
  reasoning: string;
  breakdown?: {
    semantic_score: number;
    experience_score: number;
    product_score: number;
    behavioral_score: number;
    preferred_score: number;
    location_score: number;
    must_have_score: number;
  };
}

export interface WeightSet {
  semantic_match: number;
  experience_fit: number;
  product_company: number;
  behavioral_signals: number;
  preferred_skills: number;
  location: number;
}

export interface PipelineStats {
  total_candidates: number;
  honeypots_removed: number;
  consulting_only_removed: number;
  role_filtered: number;
  experience_filtered: number;
  valid_stage1: number;
  stage1_count: number;
  stage2_count: number;
  stage3_count: number;
  final_count: number;
  runtime_seconds: number;
}

export interface EvaluationMetrics {
  ndcg_10: number;
  ndcg_100: number;
  mrr: number;
  precision_10: number;
  precision_100: number;
  recall_100: number;
}

export interface UnitTestResult {
  id: string;
  name: string;
  status: "PASS" | "FAIL";
  duration_ms: number;
  description: string;
}
