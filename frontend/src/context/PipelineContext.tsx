import React, { createContext, useContext, useState, useEffect } from "react";
import { Candidate, WeightSet, PipelineStats, EvaluationMetrics, UnitTestResult } from "../types";
import {
  candidates as initialCandidates,
  pipelineStats as initialStats,
  evaluationMetrics as initialMetrics,
  unitTests as initialTests,
  jobDescriptionText
} from "../utils/mockData";

interface PipelineContextType {
  loadedCandidates: Candidate[];
  selectedCandidate: Candidate | null;
  setSelectedCandidate: (cand: Candidate | null) => void;
  weights: WeightSet;
  setWeights: (w: WeightSet) => void;
  isAnalyzing: boolean;
  setIsAnalyzing: (b: boolean) => void;
  pipelineStats: PipelineStats;
  metrics: EvaluationMetrics;
  unitTests: UnitTestResult[];
  runRecalculate: () => void;
  jdText: string;
  setJdText: (text: string) => void;
  isDrawerOpen: boolean;
  setIsDrawerOpen: (b: boolean) => void;
  currentPage: number;
  setCurrentPage: (p: number) => void;
}

const PipelineContext = createContext<PipelineContextType | undefined>(undefined);

export const PipelineProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [loadedCandidates, setLoadedCandidates] = useState<Candidate[]>(initialCandidates);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState<boolean>(false);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [jdText, setJdText] = useState<string>(jobDescriptionText);
  const [pipelineStats] = useState<PipelineStats>(initialStats);
  const [metrics, setMetrics] = useState<EvaluationMetrics>(initialMetrics);
  const [unitTests] = useState<UnitTestResult[]>(initialTests);

  const [weights, setWeights] = useState<WeightSet>({
    semantic_match: 35,
    experience_fit: 15,
    product_company: 15,
    behavioral_signals: 15,
    preferred_skills: 10,
    location: 10,
  });

  // Select first candidate by default
  useEffect(() => {
    if (loadedCandidates.length > 0 && !selectedCandidate) {
      setSelectedCandidate(loadedCandidates[0]);
    }
  }, [loadedCandidates, selectedCandidate]);

  const runRecalculate = () => {
    setIsAnalyzing(true);
    
    // Simulate brief network/compute latency for YC feel
    setTimeout(() => {
      const wSemantic = weights.semantic_match / 100;
      const wExp = weights.experience_fit / 100;
      const wProduct = weights.product_company / 100;
      const wBeh = weights.behavioral_signals / 100;
      const wPref = weights.preferred_skills / 100;
      const wLoc = weights.location / 100;

      const updated = initialCandidates.map((cand) => {
        const breakdown = cand.breakdown || {
          semantic_score: 0.8,
          experience_score: 1.0,
          product_score: 1.0,
          behavioral_score: 0.5,
          preferred_score: 0.0,
          location_score: 1.0,
          must_have_score: 0.0,
        };

        // Recompute the scoring logic
        let rawScore = (
          wSemantic * (breakdown.semantic_score) +
          wExp * (breakdown.experience_score) +
          wProduct * (breakdown.product_score) +
          wBeh * (breakdown.behavioral_score) +
          wPref * (breakdown.preferred_score) +
          wLoc * (breakdown.location_score)
        );

        if (breakdown.must_have_score > 0.20) {
          rawScore += 0.25;
        }

        return {
          ...cand,
          fused_score: rawScore,
          score: rawScore, // Sync for table compatibility
        };
      });

      // Sort by score desc, then by candidate_id asc
      updated.sort((a, b) => {
        const diff = (b.fused_score || 0) - (a.fused_score || 0);
        if (Math.abs(diff) > 1e-9) return diff;
        return a.candidate_id.localeCompare(b.candidate_id);
      });

      // Re-assign ranks
      const ranked = updated.map((cand, idx) => ({
        ...cand,
        rank: idx + 1,
      }));

      // Update candidates and preserve selection index
      setLoadedCandidates(ranked);
      
      const currentSelected = selectedCandidate;
      if (currentSelected) {
        const matched = ranked.find((c) => c.candidate_id === currentSelected.candidate_id);
        if (matched) {
          setSelectedCandidate(matched);
        } else {
          setSelectedCandidate(ranked[0]);
        }
      } else {
        setSelectedCandidate(ranked[0]);
      }

      // Recompute metrics based on new ranks
      // We will count how many "strong fits" (original breakdown.must_have_score > 0.2 && exp between 5 and 9) are in top 10 and top 100
      let strongFitCountTop10 = 0;
      let strongFitCountTop100 = 0;
      
      ranked.forEach((cand, idx) => {
        const exp = cand.years_of_experience;
        const skillOverlap = cand.breakdown?.must_have_score || 0.0;
        const isStrong = exp >= 5.0 && exp <= 9.0 && skillOverlap > 0.20;
        
        if (isStrong) {
          if (idx < 10) strongFitCountTop10++;
          if (idx < 100) strongFitCountTop100++;
        }
      });

      const prec10 = strongFitCountTop10 / 10;
      const prec100 = strongFitCountTop100 / 100;
      
      // Calculate MRR
      let firstStrongIdx = ranked.findIndex((cand) => {
        const exp = cand.years_of_experience;
        const skillOverlap = cand.breakdown?.must_have_score || 0.0;
        return exp >= 5.0 && exp <= 9.0 && skillOverlap > 0.20;
      });
      const newMrr = firstStrongIdx !== -1 ? 1 / (firstStrongIdx + 1) : 0;

      setMetrics({
        ...initialMetrics,
        precision_10: prec10,
        precision_100: prec100,
        mrr: newMrr,
      });

      setIsAnalyzing(false);
    }, 800);
  };

  return (
    <PipelineContext.Provider
      value={{
        loadedCandidates,
        selectedCandidate,
        setSelectedCandidate,
        weights,
        setWeights,
        isAnalyzing,
        setIsAnalyzing,
        pipelineStats,
        metrics,
        unitTests,
        runRecalculate,
        jdText,
        setJdText,
        isDrawerOpen,
        setIsDrawerOpen,
        currentPage,
        setCurrentPage
      }}
    >
      {children}
    </PipelineContext.Provider>
  );
};

export const usePipeline = () => {
  const context = useContext(PipelineContext);
  if (context === undefined) {
    throw new Error("usePipeline must be used within a PipelineProvider");
  }
  return context;
};
