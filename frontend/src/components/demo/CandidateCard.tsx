import React, { useEffect, useState } from "react";
import { Candidate } from "../../data";

interface CandidateCardProps {
  candidate: Candidate;
  onClick: () => void;
}

export const CandidateCard: React.FC<CandidateCardProps> = ({ candidate, onClick }) => {
  const [fillPercent, setFillPercent] = useState(0);

  useEffect(() => {
    // Smooth transition score filling on load
    const timeout = setTimeout(() => {
      // Scale evaluation scores (0.95 - 1.06) to (25% - 100%) for visualization
      const calculatedPct = Math.min(100, Math.max(20, ((candidate.score - 0.9) / 0.2) * 100));
      setFillPercent(calculatedPct);
    }, 150);

    return () => clearTimeout(timeout);
  }, [candidate]);

  const getRankLabel = (rank: number) => {
    if (rank === 1) return "🥇";
    if (rank === 2) return "🥈";
    if (rank === 3) return "🥉";
    return `#${rank}`;
  };

  const getNoticeBadgeColors = (days: number) => {
    if (days === 0) return "bg-green-500/10 border-green-500/20 text-green-400";
    if (days <= 30) return "bg-sky-500/10 border-sky-500/20 text-sky-400";
    return "bg-amber-500/10 border-amber-500/20 text-amber-400"; // 90 days warning
  };

  return (
    <div
      onClick={onClick}
      className="glass-panel p-5 rounded-2xl border border-brand-border/60 bg-slate-900/40 hover:bg-slate-800/30 cursor-pointer transition-all duration-300 flex flex-col justify-between select-none relative group overflow-hidden"
    >
      {/* Glow background on hover */}
      <div className="absolute inset-0 bg-gradient-to-tr from-brand-purple/5 to-brand-indigo/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />

      {/* Header Info */}
      <div className="flex items-start justify-between gap-4 relative z-10">
        <div className="flex items-center gap-3">
          {/* Rank Badge */}
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-black text-xs border ${
            candidate.rank === 1
              ? "bg-amber-500/15 border-amber-500/30 text-amber-400 text-sm"
              : candidate.rank <= 3 
                ? "bg-brand-indigo/15 border-brand-indigo/30 text-white text-sm" 
                : "bg-slate-850 border-brand-indigo/20 text-brand-gray"
          }`}>
            {getRankLabel(candidate.rank)}
          </div>

          <div>
            <span className="font-extrabold text-xs text-white block tracking-tight">
              {candidate.candidate_id}
            </span>
            <span className="text-[9px] text-brand-gray font-semibold block mt-0.5 leading-none">
              {candidate.headline}
            </span>
          </div>
        </div>

        {/* Notice period */}
        <span className={`text-[9px] px-2.5 py-0.5 rounded-full border font-bold uppercase tracking-wider ${getNoticeBadgeColors(candidate.notice_period)}`}>
          Notice: {candidate.notice_period}d
        </span>
      </div>

      {/* Reasoning summary text */}
      <p className="text-slate-300 text-[10px] my-3.5 leading-relaxed line-clamp-2 italic font-medium relative z-10">
        "{candidate.reasoning}"
      </p>

      {/* Score bar */}
      <div className="space-y-1 relative z-10">
        <div className="flex justify-between text-[10px] font-bold">
          <span className="text-brand-gray">Evaluation Score</span>
          <span className="text-indigo-400 font-mono">{candidate.score.toFixed(6)}</span>
        </div>
        <div className="w-full h-1.5 bg-slate-850 rounded-full overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-indigo-500 to-teal-400 rounded-full transition-all duration-1000 ease-out"
            style={{ width: `${fillPercent}%` }}
          />
        </div>
      </div>

      {/* Skills chips list */}
      <div className="flex flex-wrap gap-1.5 mt-4 pt-3 border-t border-brand-border/40 relative z-10">
        {candidate.skills.map((sk) => (
          <span 
            key={sk}
            className="text-[9px] bg-brand-purple/10 border border-brand-purple/20 text-brand-purple px-2 py-0.5 rounded font-bold uppercase tracking-wider"
          >
            {sk}
          </span>
        ))}
      </div>
    </div>
  );
};
