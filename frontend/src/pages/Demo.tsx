import React, { useState } from "react";
import { candidatesData, Candidate } from "../data";
import { LiveFunnelCounter } from "../components/demo/LiveFunnelCounter";
import { PipelineVisualizer } from "../components/demo/PipelineVisualizer";
import { SearchFilterBar } from "../components/demo/SearchFilterBar";
import { CandidateCard } from "../components/demo/CandidateCard";
import { ScoreModal } from "../components/demo/ScoreModal";

export const Demo: React.FC = () => {
  const [filters, setFilters] = useState({ search: "", notice: "all", minScore: 0.95 });
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);

  const handleFilterChange = (newFilters: { search: string; notice: string; minScore: number }) => {
    setFilters(newFilters);
  };

  // Dynamic real-time filter computations
  const filteredCandidates = candidatesData.filter((cand) => {
    // Minimum score slider boundary
    if (cand.score < filters.minScore) return false;

    // Notice period categorization matching
    if (filters.notice !== "all") {
      const targetNotice = parseInt(filters.notice, 10);
      if (cand.notice_period !== targetNotice) return false;
    }

    // Smart string text search over skills list, headline, and reasoning dossier strings
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
      <LiveFunnelCounter />

      {/* FEATURE 3: Pipeline Visualization */}
      <PipelineVisualizer />

      {/* FEATURE 5: Search & Filter Bar */}
      <SearchFilterBar onFilterChange={handleFilterChange} />

      {/* FEATURE 1: Candidate Cards */}
      <div className="w-full mt-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider">
            Evaluated Candidate Shortlist ({filteredCandidates.length})
          </h3>
          <span className="text-[9px] bg-brand-teal/10 border border-brand-teal/20 text-brand-teal px-2.5 py-1 rounded-full font-bold uppercase tracking-wider">
            Offline verified ranks
          </span>
        </div>

        {filteredCandidates.length === 0 ? (
          <div className="glass-panel p-12 text-center rounded-2xl border border-brand-border/60 text-brand-gray text-xs">
            No candidates match the specified search filters. Try relaxing your constraints.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCandidates.map((cand) => (
              <CandidateCard 
                key={cand.candidate_id} 
                candidate={cand} 
                onClick={() => setSelectedCandidate(cand)}
              />
            ))}
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
