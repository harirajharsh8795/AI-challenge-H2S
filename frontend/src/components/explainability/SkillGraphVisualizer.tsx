import React from "react";
import { Candidate } from "../../types";
import { Network, HelpCircle, ArrowRight } from "lucide-react";

interface SkillGraphVisualizerProps {
  candidate: Candidate;
}

export const SkillGraphVisualizer: React.FC<SkillGraphVisualizerProps> = ({ candidate }) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h5 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
          <Network className="w-4 h-4 text-brand-orange" />
          <span>Skill Graph Match Traces</span>
        </h5>
        
        {/* Synonym Hops Help */}
        <div className="group relative cursor-help">
          <HelpCircle className="w-3.5 h-3.5 text-slate-500 hover:text-white" />
          <div className="absolute right-0 top-6 w-52 p-3 rounded-lg bg-slate-900 border border-slate-700 text-[10px] text-brand-gray hidden group-hover:block z-30 shadow-xl leading-relaxed">
            <span className="font-bold text-white block mb-1">BFS Synonym Decay:</span>
            * Distance 0 (Direct): Multiplier = 1.0<br/>
            * Distance 1 (1 Hop): Multiplier = 0.8<br/>
            * Distance 2 (2 Hops): Multiplier = 0.64
          </div>
        </div>
      </div>

      <div className="space-y-3">
        {/* Direct Matches */}
        <div className="space-y-1.5">
          <span className="text-[10px] text-brand-teal font-semibold uppercase tracking-wider block">
            Direct Matches (Distance 0)
          </span>
          <div className="flex flex-wrap gap-1.5">
            {candidate.must_have_skills.map((skill) => (
              <span
                key={skill}
                className="text-[10px] bg-brand-teal/10 border border-brand-teal/20 text-brand-teal px-2 py-1 rounded-lg font-medium"
              >
                {skill}
              </span>
            ))}
            {candidate.must_have_skills.length === 0 && (
              <span className="text-[10px] text-slate-500 italic">No direct must-have matches.</span>
            )}
          </div>
        </div>

        {/* Expanded Matches */}
        <div className="space-y-1.5">
          <span className="text-[10px] text-brand-orange font-semibold uppercase tracking-wider block">
            Graph Expanded Matches (Distance 1-2)
          </span>
          <div className="flex flex-wrap gap-1.5">
            {candidate.expanded_skills.map((skill) => {
              // Simulate graph hops based on known expansion rules
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
                  className="flex items-center gap-1.5 text-[10px] bg-brand-orange/10 border border-brand-orange/20 text-brand-orange px-2.5 py-1 rounded-lg font-medium"
                >
                  <span>{skill}</span>
                  <span className="text-[9px] text-slate-500 font-normal">
                    ({hopTrace})
                  </span>
                </div>
              );
            })}
            {candidate.expanded_skills.length === 0 && (
              <span className="text-[10px] text-slate-500 italic">No synonym-expanded matches.</span>
            )}
          </div>
        </div>

        {/* Preferred matches */}
        {candidate.preferred_skills.length > 0 && (
          <div className="space-y-1.5 pt-2 border-t border-brand-border/40">
            <span className="text-[10px] text-brand-purple font-semibold uppercase tracking-wider block">
              Preferred Matches
            </span>
            <div className="flex flex-wrap gap-1.5">
              {candidate.preferred_skills.map((skill) => (
                <span
                  key={skill}
                  className="text-[10px] bg-brand-purple/10 border border-brand-purple/20 text-brand-purple px-2 py-1 rounded-lg font-medium"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
