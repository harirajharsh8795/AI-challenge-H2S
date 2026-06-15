import React, { useEffect, useState } from "react";
import { Candidate } from "../../data";

interface HeroCardProps {
  candidate: Candidate;
  onClick?: () => void;
}

export const HeroCard: React.FC<HeroCardProps> = ({ candidate, onClick }) => {
  const [expanded, setExpanded] = useState(false);
  const [ringProgress, setRingProgress] = useState(0);
  
  const scorePercent = Math.min(100, ((candidate.score - 0.9) / 0.2) * 100);
  const circumference = 2 * Math.PI * 40;
  
  useEffect(() => {
    const timeout = setTimeout(() => setRingProgress(scorePercent), 300);
    return () => clearTimeout(timeout);
  }, [scorePercent]);

  return (
    <div 
      onClick={onClick}
      className="w-full mb-6 p-6 rounded-2xl border border-amber-500/40 bg-gradient-to-r from-amber-500/5 via-slate-900/40 to-amber-500/5 relative overflow-hidden cursor-pointer hover:border-amber-400 transition-all duration-300 select-none group"
    >
      {/* Gold shimmer background */}
      <div className="absolute inset-0 bg-gradient-to-r from-amber-500/3 to-transparent pointer-events-none" />
      
      {/* BEST MATCH badge */}
      <div className="absolute top-4 right-4 flex items-center gap-1.5 bg-amber-500/15 border border-amber-500/30 text-amber-400 text-[10px] font-black px-3 py-1 rounded-full uppercase tracking-wider">
        🏆 Best Match
      </div>

      <div className="flex flex-col md:flex-row items-start gap-6 relative z-10">
        
        {/* Left: Details */}
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-lg shadow-glass-orange">
              🥇
            </div>
            <div>
              <h3 className="font-black text-white text-sm">{candidate.candidate_id}</h3>
              <p className="text-[10px] text-slate-400 font-semibold">{candidate.headline}</p>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3 mb-4">
            <div className="bg-slate-900/60 rounded-xl p-3 text-center border border-slate-700/40">
              <span className="text-[9px] text-slate-500 uppercase font-bold block">Experience</span>
              <span className="text-sm font-black text-white">{candidate.experience}y</span>
            </div>
            <div className="bg-slate-900/60 rounded-xl p-3 text-center border border-slate-700/40">
              <span className="text-[9px] text-slate-500 uppercase font-bold block">Notice</span>
              <span className="text-sm font-black text-green-400">{candidate.notice_period}d</span>
            </div>
            <div className="bg-slate-900/60 rounded-xl p-3 text-center border border-slate-700/40">
              <span className="text-[9px] text-slate-500 uppercase font-bold block">Response</span>
              <span className="text-sm font-black text-blue-400">{candidate.response_rate}%</span>
            </div>
          </div>

          <div className="flex flex-wrap gap-1.5 mb-4">
            {candidate.skills.map(sk => (
              <span key={sk} className="text-[9px] bg-green-500/10 border border-green-500/20 text-green-400 px-2.5 py-1 rounded-lg font-bold uppercase tracking-wider">
                ✓ {sk}
              </span>
            ))}
          </div>

          {/* Why #1 expandable */}
          <button
            onClick={(e) => {
              e.stopPropagation(); // Avoid opening the detail modal when toggle is clicked
              setExpanded(!expanded);
            }}
            className="text-[10px] text-amber-400 font-bold flex items-center gap-1 hover:text-amber-300 transition-colors focus:outline-none"
          >
            {expanded ? "▼" : "▶"} Why is this candidate ranked #1?
          </button>
          {expanded && (
            <p className="mt-2 text-xs text-slate-300 leading-relaxed bg-slate-900/60 p-3 rounded-xl border border-slate-700/40 animate-in slide-in-from-top-1 duration-200">
              {candidate.reasoning}
            </p>
          )}
        </div>

        {/* Right: Score Ring */}
        <div className="flex flex-col items-center gap-2 flex-shrink-0 self-center md:self-start">
          <svg width="100" height="100" className="-rotate-90">
            <circle cx="50" cy="50" r="40" fill="none" stroke="#1e293b" strokeWidth="8" />
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              stroke="url(#goldGrad)"
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={circumference - (ringProgress / 100) * circumference}
              className="transition-all duration-1000 ease-out"
            />
            <defs>
              <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#f59e0b" />
                <stop offset="100%" stopColor="#22c55e" />
              </linearGradient>
            </defs>
          </svg>
          <div className="text-center -mt-16 mb-10">
            <span className="text-lg font-black text-white">{candidate.score.toFixed(3)}</span>
            <p className="text-[9px] text-slate-500 font-bold uppercase">Fused Score</p>
          </div>
          <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">
            Rank #1 of 1,00,000
          </span>
        </div>
      </div>
    </div>
  );
};
