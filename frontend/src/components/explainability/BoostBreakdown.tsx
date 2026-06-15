import React from "react";
import { Candidate } from "../../types";
import { CheckCircle2, XCircle, ArrowUpRight } from "lucide-react";

interface BoostBreakdownProps {
  candidate: Candidate;
}

export const BoostBreakdown: React.FC<BoostBreakdownProps> = ({ candidate }) => {
  const breakdown = candidate.breakdown || {
    semantic_score: 0.8,
    experience_score: 1.0,
    product_score: 1.0,
    behavioral_score: 0.5,
    preferred_score: 0.0,
    location_score: 1.0,
    must_have_score: 0.0,
  };

  const parameters = [
    { label: "Semantic Reranking Score", value: breakdown.semantic_score, max: 1.0, color: "bg-brand-purple" },
    { label: "Experience Fit Score", value: breakdown.experience_score, max: 1.0, color: "bg-brand-teal" },
    { label: "Product Company History", value: breakdown.product_score, max: 1.0, color: "bg-brand-indigo" },
    { label: "Platform Activity & Availability", value: breakdown.behavioral_score, max: 1.0, color: "bg-amber-500" },
    { label: "Preferred Skills Overlap", value: breakdown.preferred_score, max: 1.0, color: "bg-blue-500" },
    { label: "Location Alignment", value: breakdown.location_score, max: 1.0, color: "bg-pink-500" },
  ];

  return (
    <div className="space-y-6">
      {/* Parameter List */}
      <div className="space-y-4">
        <h5 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
          Scoring Signal Vectors
        </h5>
        
        {parameters.map((param, idx) => {
          const pct = Math.max(0, Math.min(100, param.value * 100));
          return (
            <div key={idx} className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="text-brand-gray">{param.label}</span>
                <span className="font-semibold text-white">{(param.value).toFixed(2)} / {param.max.toFixed(1)}</span>
              </div>
              <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${param.color}`}
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Behavioral Signals and Boosts list */}
      <div className="space-y-3 pt-4 border-t border-brand-border">
        <h5 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
          Trust & Behavioral Signals
        </h5>

        <div className="grid grid-cols-2 gap-3">
          {/* Open to work check */}
          <div className="flex items-center gap-2 p-2.5 rounded-lg bg-slate-900/40 border border-brand-border text-xs">
            {candidate.open_to_work_flag ? (
              <CheckCircle2 className="w-4 h-4 text-brand-teal flex-shrink-0" />
            ) : (
              <XCircle className="w-4 h-4 text-slate-500 flex-shrink-0" />
            )}
            <div className="truncate">
              <span className="text-[10px] text-slate-500 block leading-tight">Status</span>
              <span className="font-semibold truncate block">Open To Work</span>
            </div>
          </div>

          {/* Response rate check */}
          <div className="flex items-center gap-2 p-2.5 rounded-lg bg-slate-900/40 border border-brand-border text-xs">
            <CheckCircle2 className="w-4 h-4 text-brand-teal flex-shrink-0" />
            <div>
              <span className="text-[10px] text-slate-500 block leading-tight">Response Rate</span>
              <span className="font-semibold text-white">
                {(candidate.recruiter_response_rate * 100).toFixed(0)}%
              </span>
            </div>
          </div>

          {/* Notice Period */}
          <div className="flex items-center gap-2 p-2.5 rounded-lg bg-slate-900/40 border border-brand-border text-xs">
            <CheckCircle2 className="w-4 h-4 text-brand-teal flex-shrink-0" />
            <div>
              <span className="text-[10px] text-slate-500 block leading-tight">Notice Period</span>
              <span className={`font-semibold ${
                candidate.notice_period_days <= 30 ? "text-brand-teal" : "text-white"
              }`}>
                {candidate.notice_period_days} Days
              </span>
            </div>
          </div>

          {/* Last Login Active */}
          <div className="flex items-center gap-2 p-2.5 rounded-lg bg-slate-900/40 border border-brand-border text-xs">
            <CheckCircle2 className="w-4 h-4 text-brand-teal flex-shrink-0" />
            <div>
              <span className="text-[10px] text-slate-500 block leading-tight">Last Active</span>
              <span className="font-semibold text-white">
                {candidate.last_active_days === 0 ? "Today" : `${candidate.last_active_days}d ago`}
              </span>
            </div>
          </div>
        </div>

        {/* Priority boosts details */}
        {breakdown.must_have_score > 0.20 && (
          <div className="flex items-start gap-2.5 p-3 rounded-xl bg-brand-teal/5 border border-brand-teal/20 text-xs text-brand-teal mt-4">
            <ArrowUpRight className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <div>
              <span className="font-bold block">Must-Have Skill Boost Applied</span>
              <span className="text-[10px] text-brand-teal/80 block mt-0.5">
                Matches &gt; 20% of must-have skills, earning a programmatic prioritization score boost of +0.25.
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
