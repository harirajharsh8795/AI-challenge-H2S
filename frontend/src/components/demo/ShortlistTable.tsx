import React from "react";
import { usePipeline } from "../../context/PipelineContext";
import { Candidate } from "../../types";
import { motion, AnimatePresence } from "framer-motion";
import { MapPin, Calendar, CheckCircle2 } from "lucide-react";

export const ShortlistTable: React.FC = () => {
  const { loadedCandidates, selectedCandidate, setSelectedCandidate, isAnalyzing, setIsDrawerOpen, currentPage } = usePipeline();

  const handleSelect = (candidate: Candidate) => {
    if (!isAnalyzing) {
      setSelectedCandidate(candidate);
      setIsDrawerOpen(true);
    }
  };

  // Slice candidates for the current page
  const startIndex = (currentPage - 1) * 7;
  const endIndex = startIndex + 7;
  const pageCandidates = loadedCandidates.slice(startIndex, endIndex);

  return (
    <div className="glass-panel rounded-2xl border border-brand-border flex flex-col w-full h-full overflow-visible">
      {/* Header Ticker */}
      <div className="p-6 border-b border-brand-border bg-slate-900/20 flex items-center justify-between flex-shrink-0">
        <div>
          <h3 className="text-sm font-bold text-white">Ranked Candidate Shortlist</h3>
          <span className="text-[10px] text-brand-gray">
            Showing top evaluated matches. Hover card for preview, click to open profile intelligence drawer.
          </span>
        </div>
        <span className="text-[10px] bg-brand-teal/10 border border-brand-teal/20 text-brand-teal px-2.5 py-1 rounded-full font-semibold flex-shrink-0">
          100% Technical Roles
        </span>
      </div>

      {/* Candidate List Container */}
      <div className="p-6 space-y-4 relative w-full flex-1 min-h-[500px]">
        {isAnalyzing && (
          <div className="absolute inset-0 bg-brand-dark/40 backdrop-blur-sm flex items-center justify-center z-20 transition-all duration-300 rounded-b-2xl">
            <div className="flex flex-col items-center gap-3">
              <div className="w-8 h-8 rounded-full border-2 border-brand-orange border-t-transparent animate-spin" />
              <span className="text-xs text-brand-gray font-medium">Re-calculating semantic rankings...</span>
            </div>
          </div>
        )}

        <AnimatePresence mode="wait">
          <motion.div
            key={currentPage}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className="space-y-4"
          >
            {pageCandidates.map((cand) => {
              const isSelected = selectedCandidate?.candidate_id === cand.candidate_id;
              const exp = cand.years_of_experience;
              const skillOverlap = cand.breakdown?.must_have_score || 0.0;
              const isStrongFit = exp >= 5.0 && exp <= 9.0 && skillOverlap > 0.20;

              return (
                <div
                  key={cand.candidate_id}
                  onClick={() => handleSelect(cand)}
                  className={`h-[110px] p-4 rounded-xl border cursor-pointer transition-all duration-300 flex items-center gap-4 justify-between relative group select-none ${
                    isSelected
                      ? "bg-slate-800/80 border-brand-orange shadow-glass-orange"
                      : "bg-slate-900/40 border-brand-border hover:border-slate-800 hover:bg-slate-800/30"
                  }`}
                >
                  {/* Left profile info */}
                  <div className="flex items-center gap-4 min-w-0 flex-1 h-full">
                    {/* Rank indicator */}
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-extrabold text-xs flex-shrink-0 ${
                      cand.rank <= 3
                        ? "bg-brand-orange text-white"
                        : "bg-slate-800 text-brand-gray"
                    }`}>
                      #{cand.rank}
                    </div>

                    {/* Profile Core */}
                    <div className="min-w-0 flex-1 flex flex-col justify-center h-full">
                      <div className="flex items-center gap-2">
                        <span className="font-extrabold text-sm text-white tracking-tight">{cand.candidate_id}</span>
                        <span className={`text-[9px] px-2 py-0.5 rounded font-bold uppercase tracking-wider ${
                          isStrongFit
                            ? "bg-brand-teal/10 text-brand-teal border border-brand-teal/20"
                            : "bg-brand-gray/10 text-brand-gray border border-brand-border"
                        }`}>
                          {isStrongFit ? "Strong Fit" : "Acceptable"}
                        </span>
                      </div>
                      <h4 className="text-xs font-semibold text-slate-300 mt-1 truncate">
                        {cand.headline}
                      </h4>
                      
                      {/* Quick badges */}
                      <div className="flex items-center gap-3 mt-2 text-[10px] text-brand-gray flex-wrap">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3 text-slate-500" />
                          {cand.years_of_experience} yrs exp
                        </span>
                        <span className="flex items-center gap-1">
                          <MapPin className="w-3 h-3 text-slate-500" />
                          {cand.location}
                        </span>
                        <span className={`flex items-center gap-1 font-medium ${
                          cand.notice_period_days <= 30 ? "text-brand-teal" : "text-brand-gray"
                        }`}>
                          Notice: {cand.notice_period_days}d
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Right score and CTA */}
                  <div className="flex items-center gap-4 flex-shrink-0 h-full justify-end">
                    <div className="text-right">
                      <span className="text-[9px] text-brand-gray block uppercase tracking-wider font-semibold">Match Score</span>
                      <span className="text-sm font-black text-brand-orange">
                        {cand.score.toFixed(4)}
                      </span>
                    </div>
                    <button className="hidden sm:flex items-center px-3.5 py-1.5 rounded-lg bg-brand-orange/10 border border-brand-orange/20 text-brand-orange font-bold text-xs hover:bg-brand-orange hover:text-white transition-all duration-300 shadow-sm">
                      Inspect
                    </button>
                  </div>

                  {/* Premium Hover Tooltip Preview */}
                  <div className="absolute left-[80px] top-[-92px] opacity-0 group-hover:opacity-100 pointer-events-none transition-all duration-250 z-40 w-[340px] p-3.5 bg-slate-950/95 border border-brand-orange/30 rounded-xl shadow-2xl backdrop-blur-md flex flex-col gap-1.5 transform scale-95 group-hover:scale-100">
                    <div className="flex justify-between items-center border-b border-brand-border pb-1">
                      <span className="font-extrabold text-[10px] text-brand-orange uppercase tracking-wider">
                        Rank #{cand.rank} Preview
                      </span>
                      <span className="text-[10px] text-brand-teal font-extrabold">
                        {`${((cand.fused_score || cand.score) * 100).toFixed(1)}%`} Match
                      </span>
                    </div>
                    <p className="text-[11px] text-white font-bold leading-normal truncate">{cand.candidate_id}</p>
                    <p className="text-[10px] text-slate-300 leading-normal line-clamp-2">{cand.headline}</p>
                    <div className="flex gap-3 text-[9px] text-brand-gray">
                      <span>Exp: {cand.years_of_experience} years</span>
                      <span>•</span>
                      <span>Notice: {cand.notice_period_days} days</span>
                      <span>•</span>
                      <span>Location: {cand.location}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
};
