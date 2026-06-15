import React, { useState, useEffect } from "react";
import { Candidate } from "../data";
import { fetchCandidates, fetchStats, CandidateAPI, StatsAPI, enrichCandidate } from "../api";
import { LiveFunnelCounter } from "../components/demo/LiveFunnelCounter";
import { PipelineVisualizer } from "../components/demo/PipelineVisualizer";
import { SearchFilterBar } from "../components/demo/SearchFilterBar";
import { CandidateCard } from "../components/demo/CandidateCard";
import { ScoreModal } from "../components/demo/ScoreModal";
import { HeroCard } from "../components/demo/HeroCard";

const ApiStatus: React.FC<{ isLive: boolean }> = ({ isLive }) => (
  <div className={`flex items-center gap-1.5 text-[9px] font-extrabold px-3 py-1 rounded-full border ${
    isLive 
      ? "bg-green-500/10 border-green-500/20 text-green-400" 
      : "bg-amber-500/10 border-amber-500/20 text-amber-400"
  }`}>
    <div className={`w-1.5 h-1.5 rounded-full ${isLive ? "bg-green-400 animate-pulse" : "bg-amber-400"}`} />
    {isLive ? "API CONNECTED" : "OFFLINE FALLBACK"}
  </div>
);

export const Demo: React.FC = () => {
  const [apiCandidates, setApiCandidates] = useState<CandidateAPI[]>([]);
  const [stats, setStats] = useState<StatsAPI | null>(null);
  const [loading, setLoading] = useState(true);
  const [isLive, setIsLive] = useState(false);

  const [filters, setFilters] = useState({ search: "", notice: "all", minScore: 0.95 });
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);

  useEffect(() => {
    const apiBase = import.meta.env.VITE_API_URL || "http://localhost:8000";
    let isApiLive = true;

    // Direct check if uvicorn API endpoint is reachable
    fetch(`${apiBase}/`)
      .then((res) => {
        if (!res.ok) isApiLive = false;
      })
      .catch(() => {
        isApiLive = false;
      })
      .finally(() => {
        Promise.all([fetchCandidates(), fetchStats()])
          .then(([cands, st]) => {
            setApiCandidates(cands);
            setStats(st);
            setIsLive(isApiLive);
            setLoading(false);
          })
          .catch(() => {
            setIsLive(false);
            setLoading(false);
          });
      });
  }, []);

  const handleFilterChange = (newFilters: { search: string; notice: string; minScore: number }) => {
    setFilters(newFilters);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 w-full gap-3">
        <div className="w-8 h-8 rounded-full border-2 border-brand-indigo border-t-transparent animate-spin" />
        <div className="text-brand-indigo animate-pulse text-xs font-bold tracking-wider uppercase">
          Connecting to Redrob Copilot API...
        </div>
      </div>
    );
  }

  // Map backend raw records to full-fidelity UI Candidate items
  const enrichedList = apiCandidates.map(enrichCandidate);

  // Dynamic filter logic
  const filteredCandidates = enrichedList.filter((cand) => {
    // Score boundary check
    if (cand.score < filters.minScore) return false;

    // Notice category check
    if (filters.notice !== "all") {
      const targetNotice = parseInt(filters.notice, 10);
      if (cand.notice_period !== targetNotice) return false;
    }

    // Keyword/Synonym matching over skills, headlines, and reasoning strings
    if (filters.search.trim() !== "") {
      const query = filters.search.toLowerCase();
      const hasSkillMatch = cand.skills.some((sk) => sk.toLowerCase().includes(query));
      const hasReasoningMatch = cand.reasoning.toLowerCase().includes(query);
      const hasHeadlineMatch = cand.headline.toLowerCase().includes(query);
      if (!hasSkillMatch && !hasReasoningMatch && !hasHeadlineMatch) return false;
    }

    return true;
  });

  return (
    <div className="flex flex-col w-full pb-12">
      {/* FEATURE 2: Live Funnel Counter */}
      <LiveFunnelCounter stats={stats} />

      {/* FEATURE 3: Pipeline Visualization */}
      <PipelineVisualizer />

      {/* FEATURE 5: Search & Filter Bar */}
      <SearchFilterBar onFilterChange={handleFilterChange} />

      {/* FEATURE 1: Candidate Cards list */}
      <div className="w-full mt-4">
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center gap-3">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">
              Evaluated Candidate Shortlist ({filteredCandidates.length})
            </h3>
            <ApiStatus isLive={isLive} />
          </div>
          <span className="text-[9px] bg-brand-teal/10 border border-brand-teal/20 text-brand-teal px-2.5 py-1 rounded-full font-bold uppercase tracking-wider">
            Offline verified ranks
          </span>
        </div>

        {filteredCandidates.length === 0 ? (
          <div className="glass-panel p-12 text-center rounded-2xl border border-brand-border/60 text-brand-gray text-xs">
            No candidates match the specified search filters. Try relaxing your constraints.
          </div>
        ) : (
          <div className="space-y-6">
            {/* FEATURE 2: Rank #1 Hero Card */}
            {filteredCandidates.length > 0 && (
              <HeroCard 
                candidate={filteredCandidates[0]} 
                onClick={() => setSelectedCandidate(filteredCandidates[0])}
              />
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredCandidates.slice(1).map((cand) => (
                <CandidateCard 
                  key={cand.candidate_id} 
                  candidate={cand} 
                  onClick={() => setSelectedCandidate(cand)}
                />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* FEATURE 4: Score Breakdown Modal */}
      {selectedCandidate && (
        <ScoreModal 
          candidate={selectedCandidate} 
          onClose={() => setSelectedCandidate(null)} 
        />
      )}
    </div>
  );
};
