import React from "react";
import { Candidate } from "../../data";
import { X, ShieldCheck } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

interface ScoreModalProps {
  candidate: Candidate;
  onClose: () => void;
}

export const ScoreModal: React.FC<ScoreModalProps> = ({ candidate, onClose }) => {
  const chartData = [
    { name: "Semantic Overlap", score: candidate.semantic_score, color: "#6366f1" },
    { name: "Skill Synonym Fit", score: candidate.skill_score, color: "#22c55e" },
    { name: "Behavioral Signal", score: candidate.behavioral_score, color: "#38bdf8" }
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-sm">
      <div className="relative w-full max-w-3xl bg-[#0f0f1a] border border-brand-border/60 rounded-2xl p-6 md:p-8 flex flex-col gap-6 shadow-2xl animate-in fade-in zoom-in duration-200">
        
        {/* Close Button */}
        <button 
          onClick={onClose}
          className="absolute right-4 top-4 p-2 text-brand-gray hover:text-white rounded-xl bg-slate-900/60 hover:bg-slate-800 transition-all border border-brand-border/40"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Modal Header */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-indigo to-brand-purple flex items-center justify-center font-bold text-white shadow-glass-indigo">
            {candidate.rank <= 3 ? "🏆" : "#"}
          </div>
          <div>
            <h3 className="font-extrabold text-sm text-white tracking-tight flex items-center gap-2">
              <span>{candidate.candidate_id}</span>
              <span className="text-[10px] bg-brand-indigo/10 border border-brand-indigo/20 text-brand-indigo px-2 py-0.5 rounded font-bold uppercase tracking-wider">
                Rank #{candidate.rank}
              </span>
            </h3>
            <p className="text-[10px] text-brand-gray mt-0.5 font-semibold uppercase tracking-wider">{candidate.headline}</p>
          </div>
        </div>

        {/* Content Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Column 1: Recharts Chart & Highlighted Skills */}
          <div className="space-y-4">
            <h4 className="text-[10px] font-bold text-brand-indigo uppercase tracking-wider">Fused Score Breakdown</h4>
            
            {/* Recharts BarChart */}
            <div className="h-44 w-full bg-slate-950/60 border border-brand-border rounded-xl p-2">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} layout="vertical" margin={{ top: 10, right: 10, left: 10, bottom: 5 }}>
                  <XAxis type="number" domain={[0, 100]} stroke="#94a3b8" fontSize={8} />
                  <YAxis dataKey="name" type="category" stroke="#94a3b8" fontSize={8} width={95} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: "#0f0f1a", borderColor: "rgba(255,255,255,0.05)" }}
                    itemStyle={{ color: "#FFF", fontSize: 9 }}
                    labelStyle={{ fontSize: 9, fontWeight: "bold" }}
                  />
                  <Bar dataKey="score" radius={[0, 4, 4, 0]} barSize={12}>
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Core Skills (green highlight) */}
            <div className="space-y-2">
              <span className="text-[9px] text-brand-gray uppercase tracking-wider font-extrabold block">Matched Core Skills</span>
              <div className="flex flex-wrap gap-1.5">
                {candidate.skills.map((sk) => (
                  <span 
                    key={sk}
                    className="text-[10px] bg-green-500/10 border border-green-500/25 text-green-400 px-3 py-1 rounded-lg font-bold flex items-center gap-1 shadow-sm"
                  >
                    <ShieldCheck className="w-3.5 h-3.5" />
                    {sk}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Column 2: Selection Reasoning & Dossier Overview */}
          <div className="space-y-4 flex flex-col justify-between">
            <div className="space-y-4">
              <h4 className="text-[10px] font-bold text-brand-indigo uppercase tracking-wider">AI Selection Insights</h4>
              
              {/* Detailed Reasoning block */}
              <div className="p-4 rounded-xl bg-brand-purple/5 border border-brand-purple/10 relative">
                <p className="text-xs text-slate-300 leading-relaxed font-medium">
                  {candidate.reasoning}
                </p>
              </div>
            </div>

            {/* Dossier Specs */}
            <div className="grid grid-cols-3 gap-3 border-t border-brand-border/40 pt-4 text-center">
              <div>
                <span className="text-[9px] text-brand-gray block uppercase font-bold tracking-wider">Experience</span>
                <span className="text-xs font-black text-white mt-1 block">{candidate.experience} Years</span>
              </div>
              <div>
                <span className="text-[9px] text-brand-gray block uppercase font-bold tracking-wider">Location</span>
                <span className="text-xs font-black text-white mt-1 block truncate">{candidate.location}</span>
              </div>
              <div>
                <span className="text-[9px] text-brand-gray block uppercase font-bold tracking-wider">Response Rate</span>
                <span className="text-xs font-black text-sky-400 mt-1 block font-mono">{candidate.response_rate}%</span>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};
