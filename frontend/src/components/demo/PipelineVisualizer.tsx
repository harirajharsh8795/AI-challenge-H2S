import React, { useEffect, useState } from "react";
import { ChevronRight } from "lucide-react";

export const PipelineVisualizer: React.FC = () => {
  const [activeStage, setActiveStage] = useState(0);

  const stages = [
    { label: "Filter Stage", val: "100K → 33,310", desc: "Honeypot & Experience Checks" },
    { label: "BM25 (S1)", val: "33,310 → 2,000", desc: "Lexical Sparse Retrieval" },
    { label: "Bi-Encoder (S2)", val: "2,000 → 500", desc: "Dense Vector Similarity" },
    { label: "Cross-Encoder (S3)", val: "500 → 150", desc: "Contextual Cross-Attention" },
    { label: "Behavioral Fusion", val: "150 → 100", desc: "Availability & Activity Signals" }
  ];

  useEffect(() => {
    // Sequentially highlight each stage on load
    const interval = setInterval(() => {
      setActiveStage((prev) => {
        if (prev < stages.length - 1) {
          return prev + 1;
        } else {
          clearInterval(interval);
          return prev;
        }
      });
    }, 350); // Next stage highlight after 350ms

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="glass-panel p-6 rounded-2xl border border-brand-border/60 bg-slate-900/20 mb-6 w-full">
      <h4 className="text-[10px] font-bold text-brand-indigo uppercase tracking-wider mb-4 text-center sm:text-left">
        Platform Funnel Optimization Pipeline
      </h4>
      
      <div className="flex flex-col md:flex-row items-stretch justify-between gap-3 w-full">
        {stages.map((st, idx) => {
          const isHighlighted = idx <= activeStage;
          const isCurrent = idx === activeStage;
          return (
            <React.Fragment key={idx}>
              <div 
                className={`flex-1 p-4 rounded-xl border transition-all duration-300 flex flex-col justify-between ${
                  isCurrent 
                    ? "bg-brand-indigo/10 border-brand-indigo shadow-[0_0_15px_rgba(99,102,241,0.35)] scale-[1.02]" 
                    : isHighlighted 
                      ? "bg-slate-900/60 border-brand-teal/40" 
                      : "bg-slate-900/10 border-brand-border/40 opacity-40"
                }`}
              >
                <div>
                  <div className="text-[9px] text-brand-gray uppercase tracking-wider font-extrabold flex justify-between items-center">
                    <span>Stage {idx + 1}</span>
                    {isHighlighted && <span className="text-brand-teal font-black animate-pulse">●</span>}
                  </div>
                  <div className="font-extrabold text-xs text-white mt-1">
                    {st.label}
                  </div>
                </div>
                <div className="mt-3">
                  <div className="text-xs font-black text-sky-400">
                    {st.val}
                  </div>
                  <div className="text-[9px] text-slate-400 mt-1 leading-normal">
                    {st.desc}
                  </div>
                </div>
              </div>
              
              {idx < stages.length - 1 && (
                <div className="flex-shrink-0 flex items-center justify-center">
                  <ChevronRight 
                    className={`w-5 h-5 hidden md:block transition-all duration-300 ${
                      idx < activeStage 
                        ? "text-brand-indigo animate-pulse" 
                        : "text-slate-700"
                    }`} 
                  />
                  <div className={`w-0.5 h-4 md:hidden transition-all duration-300 ${
                    idx < activeStage 
                      ? "bg-brand-indigo" 
                      : "bg-slate-700"
                  }`} />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};
