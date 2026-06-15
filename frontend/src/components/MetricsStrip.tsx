import React from "react";

export const MetricsStrip: React.FC = () => (
  <div className="fixed bottom-0 left-0 right-0 z-40 bg-slate-950/95 backdrop-blur border-t border-slate-800/60 px-6 py-2.5 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-[10px] font-bold text-slate-300">
    <span className="text-slate-500 uppercase tracking-wider">Verified Metrics:</span>
    <span className="text-indigo-400">NDCG@10 = <span className="text-white">1.0000</span></span>
    <span className="text-slate-600 hidden sm:inline">|</span>
    <span className="text-purple-400">LLM-Judge NDCG = <span className="text-white font-mono">0.8708</span></span>
    <span className="text-slate-600 hidden sm:inline">|</span>
    <span className="text-green-400">P@10 = <span className="text-white">100%</span></span>
    <span className="text-slate-600 hidden sm:inline">|</span>
    <span className="text-sky-400">Runtime = <span className="text-white">193.94s</span></span>
    <span className="text-slate-600 hidden sm:inline">|</span>
    <span className="text-indigo-400">RAM = <span className="text-white font-mono">&lt; 150MB</span></span>
    <span className="text-slate-600 hidden sm:inline">|</span>
    <span className="text-slate-400 font-normal">CPU-Only • Fully Offline</span>
  </div>
);
