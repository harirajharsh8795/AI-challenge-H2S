import React from "react";
import { motion } from "framer-motion";

export const FunnelVisualizer: React.FC = () => {
  const stages = [
    { label: "Raw Talent Pool", count: 100000, color: "from-slate-700 to-slate-800", width: "100%", pct: "100%" },
    { label: "Technical Role Headline Filter", count: 36063, color: "from-red-600 to-orange-600", width: "85%", pct: "36.1%" },
    { label: "Consulting & Honeypot Exclusions", count: 28972, color: "from-amber-600 to-yellow-600", width: "70%", pct: "29.0%" },
    { label: "Experience Bounds [5.0 - 9.0]", count: 14217, color: "from-teal-600 to-green-600", width: "55%", pct: "14.2%" },
    { label: "Stage 1: Sparse Retrieval (BM25)", count: 2000, color: "from-blue-600 to-indigo-600", width: "40%", pct: "2.0%" },
    { label: "Stage 2: Dense Reranking (Bi-Encoder)", count: 500, color: "from-indigo-600 to-purple-600", width: "28%", pct: "0.5%" },
    { label: "Stage 3: Contextual Reranking (Cross-Encoder)", count: 150, color: "from-purple-600 to-pink-600", width: "18%", pct: "0.15%" },
    { label: "Stage 4: Behavioral Score & Must-Have Boost", count: 100, color: "from-brand-orange to-pink-500", width: "12%", pct: "0.1%" }
  ];

  return (
    <div className="glass-panel p-8 rounded-2xl border border-brand-border h-full flex flex-col justify-between relative overflow-hidden">
      {/* Background glowing gradients */}
      <div className="absolute -right-32 -top-32 w-64 h-64 bg-brand-orange/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -left-32 -bottom-32 w-64 h-64 bg-brand-purple/10 rounded-full blur-3xl pointer-events-none" />

      <div>
        <h3 className="text-xl font-bold mb-2 bg-gradient-to-r from-white to-brand-gray bg-clip-text text-transparent">
          Talent Filtration Pipeline
        </h3>
        <p className="text-sm text-brand-gray mb-8">
          Watch 100,000 resumes refine programmatically into the Top 100 Technical Candidates.
        </p>
      </div>

      <div className="flex flex-col gap-3 items-center relative z-10">
        {stages.map((stage, idx) => {
          return (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.5, delay: idx * 0.1 }}
              style={{ width: stage.width }}
              className="group cursor-default relative"
            >
              {/* Funnel Layer Segment */}
              <div className={`p-3 rounded-xl bg-gradient-to-r ${stage.color} hover:brightness-110 transition-all duration-300 flex items-center justify-between shadow-lg`}>
                <div className="flex flex-col truncate pr-2">
                  <span className="text-xs font-bold text-white group-hover:translate-x-1 transition-transform duration-300 truncate">
                    {stage.label}
                  </span>
                  <span className="text-[10px] text-white/70">
                    Step {idx + 1}
                  </span>
                </div>
                
                <div className="text-right flex-shrink-0">
                  <span className="text-sm font-black text-white block">
                    {stage.count.toLocaleString()}
                  </span>
                  <span className="text-[9px] bg-black/30 px-1.5 py-0.5 rounded text-white font-semibold">
                    {stage.pct}
                  </span>
                </div>
              </div>
              
              {/* Connector line between steps */}
              {idx < stages.length - 1 && (
                <div className="h-2 w-0.5 bg-slate-700/80 mx-auto" />
              )}
            </motion.div>
          );
        })}
      </div>

      <div className="mt-8 text-center text-xs text-brand-gray border-t border-brand-border/50 pt-4">
        All filtering operations execute 100% locally in <span className="text-white font-bold">193.94s</span> on a single CPU core.
      </div>
    </div>
  );
};
