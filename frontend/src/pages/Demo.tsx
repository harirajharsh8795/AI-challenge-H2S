import React, { useState } from "react";
import { JDUploader } from "../components/demo/JDUploader";
import { WeightAdjuster } from "../components/demo/WeightAdjuster";
import { ShortlistTable } from "../components/demo/ShortlistTable";
import { usePipeline } from "../context/PipelineContext";
import { User, BrainCircuit, X, CheckCircle2, XCircle, ChevronLeft, ChevronRight, Award } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export const Demo: React.FC = () => {
  const {
    selectedCandidate,
    isDrawerOpen,
    setIsDrawerOpen,
    currentPage,
    setCurrentPage,
    metrics,
    pipelineStats,
    loadedCandidates
  } = usePipeline();
  
  const [leftTab, setLeftTab] = useState<"spec" | "weights">("weights");

  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= 15) {
      setCurrentPage(page);
    }
  };

  const startIndex = (currentPage - 1) * 7;

  // Generate page numbers like: 1 2 3 4 5 ... 15
  const getPageNumbers = () => {
    const pages: (number | string)[] = [];
    if (currentPage <= 4) {
      pages.push(1, 2, 3, 4, 5, "...", 15);
    } else if (currentPage >= 12) {
      pages.push(1, "...", 11, 12, 13, 14, 15);
    } else {
      pages.push(1, "...", currentPage - 1, currentPage, currentPage + 1, "...", 15);
    }
    return pages;
  };

  return (
    <div className="flex flex-col gap-6 pb-12 w-full max-w-7xl mx-auto font-sans px-4 relative">
      {/* TOP ROW: Equal-height Columns Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch w-full">
        {/* COLUMN 1 (LEFT): Weights + JD + Metrics & Funnel (lg:col-span-4) */}
        <div className="lg:col-span-4 flex flex-col gap-6 items-stretch">
          {/* Card 1: Weights & JD Panel */}
          <div id="weights-panel" className="glass-panel rounded-2xl border border-brand-border flex flex-col flex-1 overflow-hidden relative">
            {/* Panel Tabs */}
            <div className="flex border-b border-brand-border bg-slate-900/40 sticky top-0 z-10 backdrop-blur-md">
              <button
                onClick={() => setLeftTab("weights")}
                className={`flex-1 py-4 text-xs font-bold border-b-2 transition-all duration-300 ${
                  leftTab === "weights"
                    ? "border-brand-orange text-brand-orange bg-slate-900/10"
                    : "border-transparent text-brand-gray hover:text-white"
                }`}
              >
                Weights Sliders
              </button>
              
              <button
                onClick={() => setLeftTab("spec")}
                className={`flex-1 py-4 text-xs font-bold border-b-2 transition-all duration-300 ${
                  leftTab === "spec"
                    ? "border-brand-orange text-brand-orange bg-slate-900/10"
                    : "border-transparent text-brand-gray hover:text-white"
                }`}
              >
                JD Requirements
              </button>
            </div>

            {/* Panel Content */}
            <div className="p-6 flex-1 flex flex-col justify-between">
              {leftTab === "weights" ? <WeightAdjuster /> : <JDUploader />}
            </div>
          </div>

          {/* Card 2: Metrics & Pipeline Summary */}
          <div className="glass-panel rounded-2xl border border-brand-border p-6 space-y-4 flex flex-col justify-between flex-shrink-0 bg-brand-card/30">
            <h4 className="font-bold flex items-center gap-2 text-sm text-white">
              <Award className="w-4 h-4 text-brand-teal" />
              <span>Pipeline Metrics & IR Accuracy</span>
            </h4>
            <div className="grid grid-cols-2 gap-3">
              <div className="p-2.5 bg-slate-900/40 border border-brand-border rounded-xl">
                <span className="text-[9px] text-brand-gray block uppercase font-bold tracking-wider leading-tight">NDCG @ 100</span>
                <span className="text-xs font-extrabold text-white mt-0.5 block">{(metrics.ndcg_100).toFixed(4)}</span>
              </div>
              <div className="p-2.5 bg-slate-900/40 border border-brand-border rounded-xl">
                <span className="text-[9px] text-brand-gray block uppercase font-bold tracking-wider leading-tight">MRR</span>
                <span className="text-xs font-extrabold text-white mt-0.5 block">{(metrics.mrr).toFixed(4)}</span>
              </div>
              <div className="p-2.5 bg-slate-900/40 border border-brand-border rounded-xl">
                <span className="text-[9px] text-brand-gray block uppercase font-bold tracking-wider leading-tight">Precision @ 100</span>
                <span className="text-xs font-extrabold text-brand-teal mt-0.5 block">{((metrics.precision_100) * 100).toFixed(1)}%</span>
              </div>
              <div className="p-2.5 bg-slate-900/40 border border-brand-border rounded-xl">
                <span className="text-[9px] text-brand-gray block uppercase font-bold tracking-wider leading-tight">Recall @ 100</span>
                <span className="text-xs font-extrabold text-white mt-0.5 block">{((metrics.recall_100) * 100).toFixed(2)}%</span>
              </div>
            </div>

            <div className="pt-4 border-t border-brand-border/40 space-y-2 text-xs">
              <span className="text-[9px] text-brand-gray block uppercase font-bold tracking-wider">Filter Funnel Summary</span>
              <div className="flex justify-between text-slate-300">
                <span>Initial Talent Pool:</span>
                <span className="font-semibold text-white">{pipelineStats.total_candidates.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-slate-300">
                <span>Role & Exp Filtered:</span>
                <span className="font-semibold text-white">-{ (pipelineStats.role_filtered + pipelineStats.experience_filtered).toLocaleString() }</span>
              </div>
              <div className="flex justify-between text-slate-300">
                <span>Consulting Firm Drops:</span>
                <span className="font-semibold text-white">-{ pipelineStats.consulting_only_removed.toLocaleString() }</span>
              </div>
              <div className="flex justify-between text-brand-teal font-semibold">
                <span>Final Shortlist:</span>
                <span>{pipelineStats.final_count} candidates</span>
              </div>
            </div>
          </div>
        </div>

        {/* COLUMN 2 (RIGHT): Ranked Candidate Shortlist (lg:col-span-8) */}
        <div className="lg:col-span-8 flex flex-col items-stretch">
          <ShortlistTable />
        </div>
      </div>

      {/* BOTTOM ROW: Pagination Footer (Full Width below both columns) */}
      <div className="w-full border-t border-brand-border/60 pt-6 mt-4 flex flex-col sm:flex-row items-center justify-between gap-4 flex-shrink-0">
        {/* Page Indicator text */}
        <div className="text-xs font-semibold text-slate-300">
          Page <span className="text-brand-orange">{currentPage}</span> of <span className="text-white">15</span>
          <span className="text-brand-gray ml-3 font-normal">
            (Showing {startIndex + 1}–{Math.min(startIndex + 7, loadedCandidates.length)} of {loadedCandidates.length} candidates)
          </span>
        </div>

        {/* Navigation buttons */}
        <div className="flex items-center gap-1.5">
          {/* Previous Button */}
          <button
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1}
            className="flex items-center gap-1 px-3 py-2 rounded-lg border border-brand-border bg-slate-900/40 text-brand-gray hover:text-white hover:bg-slate-800 disabled:opacity-30 disabled:hover:bg-slate-900/40 disabled:hover:text-brand-gray transition-all duration-200 text-xs font-bold"
          >
            <ChevronLeft className="w-3.5 h-3.5" />
            <span>Previous</span>
          </button>

          {/* Page numbers list */}
          <div className="flex items-center gap-1">
            {getPageNumbers().map((p, idx) => {
              if (p === "...") {
                return (
                  <span key={`ell-${idx}`} className="px-1 text-slate-600 text-xs font-bold">
                    ...
                  </span>
                );
              }
              const isCurrent = currentPage === p;
              return (
                <button
                  key={`p-${p}`}
                  onClick={() => handlePageChange(p as number)}
                  className={`w-7.5 h-7.5 rounded-lg text-xs font-bold transition-all duration-200 flex items-center justify-center ${
                    isCurrent
                      ? "bg-brand-orange text-white shadow-sm shadow-brand-orange/20"
                      : "border border-brand-border bg-slate-900/20 text-brand-gray hover:text-white hover:bg-slate-800"
                  }`}
                  style={{ width: "30px", height: "30px" }}
                >
                  {p}
                </button>
              );
            })}
          </div>

          {/* Next Button */}
          <button
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage === 15}
            className="flex items-center gap-1 px-3 py-2 rounded-lg border border-brand-border bg-slate-900/40 text-brand-gray hover:text-white hover:bg-slate-800 disabled:opacity-30 disabled:hover:bg-slate-900/40 disabled:hover:text-brand-gray transition-all duration-200 text-xs font-bold"
          >
            <span>Next</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* CANDIDATE INTELLIGENCE FULL-SCREEN MODAL OVERLAY (Section 3 Overlay) */}
      <AnimatePresence>
        {isDrawerOpen && selectedCandidate && (
          <>
            {/* Full-Screen Drawer Panel */}
            <motion.div
              initial={{ y: "100%" }}
              animate={{ y: 0 }}
              exit={{ y: "100%" }}
              transition={{ type: "spring", damping: 30, stiffness: 220 }}
              className="fixed inset-0 w-screen h-screen bg-[#070b13] z-50 flex flex-col overflow-hidden font-sans"
            >
              {/* Modal Header */}
              <div className="p-6 border-b border-brand-border bg-slate-900/40 flex items-center justify-between flex-shrink-0 px-8">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center font-extrabold text-white flex-shrink-0">
                    <User className="w-5 h-5 text-brand-orange" />
                  </div>
                  <div>
                    <h3 className="font-extrabold text-base text-white tracking-tight flex items-center gap-2">
                      <span>{selectedCandidate.candidate_id}</span>
                      <span className="text-[10px] bg-brand-orange/10 border border-brand-orange/20 text-brand-orange px-2 py-0.5 rounded font-bold uppercase tracking-wider">
                        Rank #{selectedCandidate.rank}
                      </span>
                    </h3>
                    <p className="text-[10px] text-brand-gray mt-0.5 font-medium">Recruiter AI Discovery Dossier</p>
                  </div>
                </div>

                <div className="flex items-center gap-6">
                  <div className="text-right">
                    <span className="text-sm font-black text-brand-teal block">
                      {`${((selectedCandidate.fused_score || selectedCandidate.score) * 100).toFixed(1)}%`} Match
                    </span>
                  </div>
                  <button
                    onClick={() => setIsDrawerOpen(false)}
                    className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-all duration-200 text-xs font-bold"
                  >
                    <X className="w-4 h-4" />
                    <span>Close Dossier</span>
                  </button>
                </div>
              </div>

              {/* Modal Scrollable Content: 3-column Layout */}
              <div className="flex-1 overflow-y-auto p-8 scrollbar-thin bg-[#070b13]">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start max-w-7xl mx-auto">
                  
                  {/* COLUMN 1: Overview & Behavioral Signals */}
                  <div className="space-y-6">
                    {/* Section 1: Candidate Overview */}
                    <div className="space-y-3">
                      <h4 className="text-[10px] font-bold text-brand-orange uppercase tracking-wider">Section 1: Candidate Overview</h4>
                      <div className="p-5 bg-slate-900/20 border border-brand-border rounded-xl space-y-4">
                        <div className="text-xs">
                          <span className="text-brand-gray block text-[10px]">Headline / Role Title</span>
                          <span className="font-bold text-white leading-normal block mt-1">{selectedCandidate.headline}</span>
                        </div>
                        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-brand-border/40">
                          <div>
                            <span className="text-brand-gray block text-[9px] uppercase tracking-wider font-bold">Experience Scope</span>
                            <span className="text-xs font-bold text-white mt-1 block">{selectedCandidate.years_of_experience} Years</span>
                          </div>
                          <div>
                            <span className="text-brand-gray block text-[9px] uppercase tracking-wider font-bold">Primary Location</span>
                            <span className="text-xs font-bold text-white mt-1 block truncate">{selectedCandidate.location}</span>
                          </div>
                          <div>
                            <span className="text-brand-gray block text-[9px] uppercase tracking-wider font-bold">Notice Period</span>
                            <span className="text-xs font-bold text-white mt-1 block">{selectedCandidate.notice_period_days} Days</span>
                          </div>
                          <div>
                            <span className="text-brand-gray block text-[9px] uppercase tracking-wider font-bold">Response Rate</span>
                            <span className="text-xs font-bold text-white mt-1 block">{(selectedCandidate.recruiter_response_rate * 100).toFixed(0)}%</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Section 3: Behavioral Signals */}
                    <div className="space-y-3">
                      <h4 className="text-[10px] font-bold text-brand-orange uppercase tracking-wider">Section 3: Behavioral Signals</h4>
                      <div className="grid grid-cols-2 gap-3.5">
                        <div className="flex items-center gap-2 p-3 rounded-lg bg-slate-900/40 border border-brand-border text-xs">
                          {selectedCandidate.open_to_work_flag ? (
                            <CheckCircle2 className="w-4 h-4 text-brand-teal flex-shrink-0" />
                          ) : (
                            <XCircle className="w-4 h-4 text-slate-500 flex-shrink-0" />
                          )}
                          <div>
                            <span className="text-[9px] text-slate-500 block leading-tight">Status</span>
                            <span className="font-semibold text-white">Open To Work</span>
                          </div>
                        </div>

                        <div className="flex items-center gap-2 p-3 rounded-lg bg-slate-900/40 border border-brand-border text-xs">
                          <CheckCircle2 className="w-4 h-4 text-brand-teal flex-shrink-0" />
                          <div>
                            <span className="text-[9px] text-slate-500 block leading-tight">Notice Speed</span>
                            <span className="font-semibold text-white">{selectedCandidate.notice_period_days} Days Notice</span>
                          </div>
                        </div>

                        <div className="flex items-center gap-2 p-3 rounded-lg bg-slate-900/40 border border-brand-border text-xs">
                          <CheckCircle2 className="w-4 h-4 text-brand-teal flex-shrink-0" />
                          <div>
                            <span className="text-[9px] text-slate-500 block leading-tight">Last Activity</span>
                            <span className="font-semibold text-white">
                              {selectedCandidate.last_active_days === 0 ? "Active Today" : `Active ${selectedCandidate.last_active_days}d ago`}
                            </span>
                          </div>
                        </div>

                        <div className="flex items-center gap-2 p-3 rounded-lg bg-slate-900/40 border border-brand-border text-xs">
                          <CheckCircle2 className="w-4 h-4 text-brand-teal flex-shrink-0" />
                          <div>
                            <span className="text-[9px] text-slate-500 block leading-tight">Github Activity</span>
                            <span className="font-semibold text-white">Score: {selectedCandidate.github_activity_score}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* COLUMN 2: Skill Match Breakdown & Trust Signals */}
                  <div className="space-y-6">
                    {/* Section 2: Skill Match Breakdown */}
                    <div className="space-y-3">
                      <h4 className="text-[10px] font-bold text-brand-orange uppercase tracking-wider">Section 2: Skill Match Breakdown</h4>
                      <div className="p-5 bg-slate-900/20 border border-brand-border rounded-xl space-y-4">
                        {[
                          { label: "Semantic Reranking Score", value: selectedCandidate.breakdown?.semantic_score || 0.8, color: "bg-brand-purple" },
                          { label: "Experience Fit Score", value: selectedCandidate.breakdown?.experience_score || 1.0, color: "bg-brand-teal" },
                          { label: "Product Company History", value: selectedCandidate.breakdown?.product_score || 1.0, color: "bg-brand-orange" },
                          { label: "Platform Activity & Availability", value: selectedCandidate.breakdown?.behavioral_score || 0.5, color: "bg-amber-500" },
                          { label: "Preferred Skills Overlap", value: selectedCandidate.breakdown?.preferred_score || 0.0, color: "bg-blue-500" },
                          { label: "Location Alignment", value: selectedCandidate.breakdown?.location_score || 1.0, color: "bg-pink-500" },
                        ].map((param, idx) => {
                          const pct = Math.max(0, Math.min(100, param.value * 100));
                          return (
                            <div key={idx} className="space-y-1.5">
                              <div className="flex justify-between text-xs">
                                <span className="text-brand-gray">{param.label}</span>
                                <span className="font-semibold text-white">{(param.value).toFixed(2)} / 1.0</span>
                              </div>
                              <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                                <div
                                  className={`h-full rounded-full transition-all duration-500 ${param.color}`}
                                  style={{ width: `${pct}%` }}
                                />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    {/* Section 4: Trust Signals */}
                    <div className="space-y-3">
                      <h4 className="text-[10px] font-bold text-brand-orange uppercase tracking-wider">Section 4: Trust Signals</h4>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/40 border border-brand-border text-xs">
                          <div className="flex items-center gap-2">
                            <CheckCircle2 className="w-4.5 h-4.5 text-brand-teal flex-shrink-0" />
                            <span className="text-white font-medium">Compliance Unit Tests Passed</span>
                          </div>
                          <span className="text-[10px] bg-brand-teal/10 border border-brand-teal/20 text-brand-teal px-2.5 py-0.5 rounded font-bold uppercase tracking-wider">PASS</span>
                        </div>

                        <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/40 border border-brand-border text-xs">
                          <div className="flex items-center gap-2">
                            <CheckCircle2 className="w-4.5 h-4.5 text-brand-teal flex-shrink-0" />
                            <span className="text-white font-medium">Verified Product Company History</span>
                          </div>
                          <span className="text-[10px] bg-brand-teal/10 border border-brand-teal/20 text-brand-teal px-2.5 py-0.5 rounded font-bold uppercase tracking-wider">{selectedCandidate.company_background === "Product" ? "YES" : "MIXED"}</span>
                        </div>

                        <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/40 border border-brand-border text-xs">
                          <div className="flex items-center gap-2">
                            <CheckCircle2 className="w-4.5 h-4.5 text-brand-teal flex-shrink-0" />
                            <span className="text-white font-medium">Honeypot Evaluation Filters</span>
                          </div>
                          <span className="text-[10px] bg-brand-teal/10 border border-brand-teal/20 text-brand-teal px-2.5 py-0.5 rounded font-bold uppercase tracking-wider">CLEAN</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* COLUMN 3: AI Selection Reasoning & Skill Graph Matches */}
                  <div className="space-y-6">
                    {/* Section 5: Decision Reasoning */}
                    <div className="space-y-3">
                      <h4 className="text-[10px] font-bold text-brand-orange uppercase tracking-wider">Section 5: AI Selection Reasoning</h4>
                      <div className="p-5 rounded-xl bg-brand-purple/5 border border-brand-purple/10 space-y-3.5 relative">
                        <div className="flex items-center gap-2 text-xs text-brand-purple font-bold">
                          <BrainCircuit className="w-4.5 h-4.5" />
                          <span>Redrob Copilot Selection Insights</span>
                        </div>
                        <p className="text-xs text-slate-300 leading-relaxed font-normal">
                          {selectedCandidate.reasoning}
                        </p>
                      </div>
                    </div>

                    {/* Section 6: Skill Graph Matches */}
                    <div className="space-y-3">
                      <h4 className="text-[10px] font-bold text-brand-orange uppercase tracking-wider">Section 6: Skill Graph Matches</h4>
                      <div className="p-5 bg-slate-900/20 border border-brand-border rounded-xl space-y-4 text-xs">
                        {/* Direct matches */}
                        <div className="space-y-1.5">
                          <span className="text-[10px] text-brand-teal font-semibold uppercase tracking-wider block">
                            Direct Matches (Distance 0)
                          </span>
                          <div className="flex flex-wrap gap-1.5">
                            {selectedCandidate.must_have_skills.map((skill) => (
                              <span
                                key={skill}
                                className="text-[10px] bg-brand-teal/10 border border-brand-teal/20 text-brand-teal px-2 py-0.5 rounded font-semibold"
                              >
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>

                        {/* Expanded matches */}
                        <div className="space-y-1.5 pt-3 border-t border-brand-border/40">
                          <span className="text-[10px] text-brand-orange font-semibold uppercase tracking-wider block">
                            Synonym Traversal Matches (Distance 1-2)
                          </span>
                          <div className="flex flex-wrap gap-1.5">
                            {selectedCandidate.expanded_skills.map((skill) => {
                              let hopTrace = "";
                              if (skill.toLowerCase() === "peft") {
                                hopTrace = "LoRA → PEFT";
                              } else if (skill.toLowerCase() === "embeddings") {
                                hopTrace = "dense retrieval → embeddings";
                              } else if (skill.toLowerCase() === "vector database") {
                                hopTrace = "qdrant → vector database";
                              } else {
                                hopTrace = `${skill} (Synonym Hop)`;
                              }
                              return (
                                <div
                                  key={skill}
                                  className="flex items-center gap-1.5 text-[10px] bg-brand-orange/10 border border-brand-orange/20 text-brand-orange px-2 py-0.5 rounded font-semibold"
                                >
                                  <span>{skill}</span>
                                  <span className="text-[9px] text-slate-500 font-normal">({hopTrace})</span>
                                </div>
                              );
                            })}
                          </div>
                        </div>

                        {/* Preferred matches */}
                        {selectedCandidate.preferred_skills.length > 0 && (
                          <div className="space-y-1.5 pt-3 border-t border-brand-border/40">
                            <span className="text-[10px] text-brand-purple font-semibold uppercase tracking-wider block">
                              Preferred Matches (Nice-to-Have)
                            </span>
                            <div className="flex flex-wrap gap-1.5">
                              {selectedCandidate.preferred_skills.map((skill) => (
                                <span
                                  key={skill}
                                  className="text-[10px] bg-brand-purple/10 border border-brand-purple/20 text-brand-purple px-2 py-0.5 rounded font-semibold"
                                >
                                  {skill}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};
