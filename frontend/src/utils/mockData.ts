import { Candidate, PipelineStats, EvaluationMetrics, UnitTestResult } from "../types";
import candidatesRaw from "./candidates_data.json";

export const candidates: Candidate[] = candidatesRaw as Candidate[];

export const pipelineStats: PipelineStats = {
  total_candidates: 100000,
  honeypots_removed: 65,
  consulting_only_removed: 7026,
  role_filtered: 63937,
  experience_filtered: 14755,
  valid_stage1: 14217,
  stage1_count: 2000,
  stage2_count: 500,
  stage3_count: 150,
  final_count: 100,
  runtime_seconds: 193.94,
};

export const evaluationMetrics: EvaluationMetrics = {
  ndcg_10: 1.0,
  ndcg_100: 1.0,
  mrr: 1.0,
  precision_10: 1.0,
  precision_100: 1.0,
  recall_100: 0.0369,
};

export const unitTests: UnitTestResult[] = [
  {
    id: "test_schema",
    name: "Schema validation tests",
    status: "PASS",
    duration_ms: 12,
    description: "Verifies candidate_id format, rank sequence, score decay, and reasoning presence."
  },
  {
    id: "test_honeypots_rule1",
    name: "Honeypot Rule 1: Expert Skill with 0 Duration",
    status: "PASS",
    duration_ms: 8,
    description: "Catches candidates claiming expert proficiency in a skill but listing 0 duration_months."
  },
  {
    id: "test_honeypots_rule2",
    name: "Honeypot Rule 2: Career Duration Time Dilations",
    status: "PASS",
    duration_ms: 9,
    description: "Disqualifies candidates whose job duration months exceed actual elapsed calendar months by >24."
  },
  {
    id: "test_honeypots_rule3",
    name: "Honeypot Rule 3: Declared Experience Gaps",
    status: "PASS",
    duration_ms: 7,
    description: "Flags profiles claiming experience but having an empty history, or having history duration gap >3 years."
  },
  {
    id: "test_consulting_only",
    name: "Service-Only Consulting Firm Filter",
    status: "PASS",
    duration_ms: 15,
    description: "Filters out candidates whose career histories show only outsourcing service companies (TCS, Infosys, etc.)."
  },
  {
    id: "test_technical_role_filter",
    name: "Technical Title Vetting Filter",
    status: "PASS",
    duration_ms: 10,
    description: "Screens candidate headlines to allow only engineering/data-science roles and discard sales/marketing/ops."
  },
  {
    id: "test_skill_synonym_expansion",
    name: "Skill Synonym Graph BFS Traversal",
    status: "PASS",
    duration_ms: 22,
    description: "Validates BFS multi-hop synonym distances (e.g. Faiss -> Vector DB -> Vector Index) with decay multipliers."
  },
  {
    id: "test_cross_encoder_rerank",
    name: "Cross-Encoder Local CPU Reranker",
    status: "PASS",
    duration_ms: 140,
    description: "Validates local offline loading of ms-marco-MiniLM-L-6-v2 and deep query-attention semantic scoring."
  },
  {
    id: "test_behavioral_score_fusion",
    name: "Behavioral Signal & Constraints Blending",
    status: "PASS",
    duration_ms: 14,
    description: "Asserts correctness of Composite Fused Scoring, checking Relocation, Notice Period, and Login Activity boosts."
  }
];

export const jobDescriptionText = `
Role: Senior AI Engineer - Search & Discovery Infrastructure
Experience: 5-9 Years (Target), 3-12 Years (Hard limits)
Location: Noida / Pune (Hybrid, 3 days on-site) or Tier-1 India locations willing to relocate.

Requirements:
- Core technical background in Applied ML, NLP, and Information Retrieval (IR) systems.
- Hands-on experience building vector indices, dense retrieval systems, and semantic ranking functions.
- Stack: Python, PyTorch, Sentence-Transformers, Hugging Face, Qdrant, Faiss, Elasticsearch, SQL.
- Deep understanding of modern GenAI techniques: fine-tuning (LoRA, PEFT), embeddings, and RAG architectures.
- Experience running model optimization on local environments (CPU and memory constraints).
- Standard product company experience preferred (disqualify service/outsourcing agencies if candidate lists no product career).

Behavioral Signals:
- High activity and responsiveness on Redrob platform (last active within 30 days, response rate >= 70%).
- Quick notice period preferred (sub-30 days joiners receive active scoring boost).
`;

export const extractedRequirements = {
  must_have: ["Python", "Machine Learning", "NLP", "Embeddings", "Dense Retrieval", "Vector Database", "Qdrant", "Faiss", "LoRA", "PEFT", "RAG"],
  preferred: ["PyTorch", "Hugging Face", "Elasticsearch", "SQL", "Model Optimization"],
  min_experience: 5.0,
  max_experience: 9.0,
  locations: ["Noida", "Pune", "Hyderabad", "Mumbai", "Delhi NCR"]
};
