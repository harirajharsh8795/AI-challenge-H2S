import React from "react";
import { motion } from "framer-motion";
import { User, ShieldCheck, BrainCircuit, Network, Cpu, Award, Zap, CheckCircle2 } from "lucide-react";

export const WorkspacePreview: React.FC = () => {
  // Mocking the top candidate CAND_0068351
  const candidate = {
    id: "CAND_0068351",
    headline: "Senior AI Engineer - Search & Discovery Infrastructure",
    score: "1.0790",
    relevance: "98.6%",
    experience: "6.4 Years",
    company: "Scale AI (Product)",
    location: "Noida (Relocating)",
    skills: ["Python", "PyTorch", "Qdrant", "LoRA", "PEFT", "RAG"],
    expandedSkills: ["Dense Retrieval", "Vector DB", "Fine-Tuning"],
    reasoning: "Lead AI Engineer with 6.4 years of experience, matching 4 core skills (Lora, Peft, Python, Qdrant) and showing a strong product company history. Active within 90 days with a 0-day notice period and 86% response rate."
  };

  return (
    <div className="glass-panel p-6 rounded-2xl border border-brand-border h-full flex flex-col justify-between relative overflow-hidden select-none font-sans bg-slate-950/40">
      {/* Background radial glow */}
      <div className="absolute -right-24 -top-24 w-48 h-48 bg-brand-orange/15 rounded-full blur-3xl pointer-events-none animate-pulse" />
      <div className="absolute -left-24 -bottom-24 w-48 h-48 bg-brand-purple/15 rounded-full blur-3xl pointer-events-none" />

      {/* Mockup Toolbar Header */}
      <div className="flex items-center justify-between border-b border-brand-border pb-4 mb-4">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-red-500/80" />
          <span className="w-2.5 h-2.5 rounded-full bg-yellow-500/80" />
          <span className="w-2.5 h-2.5 rounded-full bg-green-500/80" />
          <span className="text-[10px] text-brand-gray ml-2 font-mono bg-slate-900/60 px-2.5 py-0.5 rounded border border-brand-border">
            redrob.ai/workspace/copilot
          </span>
        </div>
        
        {/* Badges */}
        <div className="flex items-center gap-1.5">
          <span className="flex items-center gap-0.5 text-[9px] font-bold px-2 py-0.5 rounded-full bg-brand-teal/10 border border-brand-teal/20 text-brand-teal">
            <ShieldCheck className="w-2.5 h-2.5" />
            <span>NDCG 1.0</span>
          </span>
          <span className="flex items-center gap-0.5 text-[9px] font-bold px-2 py-0.5 rounded-full bg-brand-orange/10 border border-brand-orange/20 text-brand-orange animate-pulse">
            <Cpu className="w-2.5 h-2.5" />
            <span>Offline CPU</span>
          </span>
        </div>
      </div>

      {/* Main Preview Workspace Mockup */}
      <div className="flex-1 space-y-4">
        {/* Sidebar / Profile Summary Header */}
        <div className="p-4 rounded-xl bg-slate-900/80 border border-brand-border flex items-start gap-3 shadow-md">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-tr from-brand-orange to-brand-purple flex items-center justify-center font-bold text-white flex-shrink-0 shadow-glass-orange">
            <User className="w-5 h-5 text-white" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center justify-between">
              <h4 className="font-extrabold text-xs text-white tracking-tight flex items-center gap-2">
                <span>{candidate.id}</span>
                <span className="text-[9px] bg-brand-orange/10 border border-brand-orange/20 text-brand-orange px-1.5 py-0.2 rounded font-semibold">
                  Rank #1
                </span>
              </h4>
              <div className="text-right">
                <span className="text-xs font-black text-brand-teal">{candidate.relevance} Relevance</span>
                <span className="text-[8px] text-brand-gray block">Fused: {candidate.score}</span>
              </div>
            </div>
            <p className="text-[10px] text-slate-300 font-medium truncate mt-0.5">{candidate.headline}</p>
            <div className="flex gap-3 text-[9px] text-brand-gray mt-1.5">
              <span className="flex items-center gap-1"><Award className="w-3 h-3 text-brand-orange" /> {candidate.experience}</span>
              <span className="flex items-center gap-1"><Zap className="w-3 h-3 text-brand-purple" /> {candidate.company}</span>
            </div>
          </div>
        </div>

        {/* Dynamic Skill synonym graph preview inside card */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-brand-border space-y-2.5">
          <div className="flex items-center justify-between text-[10px] text-brand-purple font-bold">
            <div className="flex items-center gap-1">
              <Network className="w-3.5 h-3.5" />
              <span>Skill Synonym Expansion (BFS)</span>
            </div>
            <span className="text-[9px] bg-brand-purple/10 px-2 py-0.5 rounded text-brand-purple">
              100% Match Ratio
            </span>
          </div>

          <div className="flex flex-wrap gap-1.5 pt-1">
            {candidate.skills.slice(0, 4).map((skill, idx) => (
              <span key={idx} className="text-[9px] font-semibold px-2 py-1 rounded bg-slate-800 border border-brand-border text-white flex items-center gap-1">
                <span className="w-1 h-1 rounded-full bg-brand-teal" />
                {skill}
              </span>
            ))}
            {candidate.expandedSkills.map((skill, idx) => (
              <span key={idx} className="text-[9px] font-semibold px-2 py-1 rounded bg-brand-purple/5 border border-brand-purple/20 text-brand-purple flex items-center gap-1">
                <span className="w-1 h-1 rounded-full bg-brand-purple animate-pulse" />
                {skill} (Expanded)
              </span>
            ))}
          </div>
        </div>

        {/* Explainability Decision bubble */}
        <div className="p-3.5 rounded-xl bg-brand-purple/5 border border-brand-purple/10 space-y-1.5 relative">
          <div className="flex items-center gap-1 text-[10px] text-brand-purple font-bold">
            <BrainCircuit className="w-3.5 h-3.5" />
            <span>AI Decision Reasoning</span>
          </div>
          <p className="text-[10px] text-slate-300 leading-relaxed font-sans italic">
            "{candidate.reasoning}"
          </p>
        </div>
      </div>

      {/* Footer Info */}
      <div className="mt-4 pt-3.5 border-t border-brand-border/60 flex items-center justify-between text-[9px] text-brand-gray">
        <span className="flex items-center gap-1">
          <CheckCircle2 className="w-3 h-3 text-brand-teal" /> Verified Top 100 Shortlist
        </span>
        <span className="text-slate-500 font-mono">193.94s CPU Execution</span>
      </div>
    </div>
  );
};
