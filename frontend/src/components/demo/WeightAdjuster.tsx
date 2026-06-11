import React from "react";
import { usePipeline } from "../../context/PipelineContext";
import { Sliders, RefreshCw, AlertTriangle } from "lucide-react";

export const WeightAdjuster: React.FC = () => {
  const { weights, setWeights, runRecalculate, isAnalyzing } = usePipeline();

  const handleSliderChange = (key: keyof typeof weights, value: number) => {
    setWeights({
      ...weights,
      [key]: value,
    });
  };

  const totalSum =
    weights.semantic_match +
    weights.experience_fit +
    weights.product_company +
    weights.behavioral_signals +
    weights.preferred_skills +
    weights.location;

  const sliderItems = [
    { key: "semantic_match", label: "Semantic Reranking", desc: "Bi + Cross-Encoder Blended Vector Match", color: "accent-brand-purple" },
    { key: "experience_fit", label: "Experience Match", desc: "Score bounds for Target [5-9 yrs] bounds", color: "accent-brand-teal" },
    { key: "product_company", label: "Product Company Background", desc: "Penalizes purely consulting history", color: "accent-brand-orange" },
    { key: "behavioral_signals", label: "Platform Activity & Availability", desc: "User engagement frequency & open to work", color: "accent-amber-500" },
    { key: "preferred_skills", label: "Preferred Skills Overlap", desc: "JD nice-to-have skill match weight", color: "accent-blue-500" },
    { key: "location", label: "Location Closeness", desc: "Hub resident Noida/Pune or relocate", color: "accent-pink-500" },
  ] as const;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b border-brand-border pb-4">
        <h4 className="font-bold flex items-center gap-2 text-sm">
          <Sliders className="w-4 h-4 text-brand-orange" />
          <span>Priority Weights Configuration</span>
        </h4>
        <div className="text-right">
          <span className={`text-xs font-semibold px-2 py-1 rounded ${totalSum === 100 ? "bg-brand-teal/10 text-brand-teal" : "bg-brand-orange/10 text-brand-orange"}`}>
            Sum: {totalSum}%
          </span>
        </div>
      </div>

      <div className="space-y-4">
        {sliderItems.map((item) => {
          const val = weights[item.key];
          return (
            <div key={item.key} className="space-y-1">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-white">{item.label}</span>
                <span className="text-brand-orange">{val}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={val}
                onChange={(e) => handleSliderChange(item.key, parseInt(e.target.value))}
                disabled={isAnalyzing}
                className={`w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer ${item.color} disabled:opacity-50`}
              />
              <span className="text-[10px] text-slate-500 block leading-tight">
                {item.desc}
              </span>
            </div>
          );
        })}
      </div>

      {totalSum !== 100 && (
        <div className="flex items-center gap-2 p-3 rounded-xl bg-brand-orange/5 border border-brand-orange/10 text-brand-orange text-[11px]">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          <span>Weights sum to {totalSum}%. Values will be normalized internally.</span>
        </div>
      )}

      <button
        onClick={runRecalculate}
        disabled={isAnalyzing}
        className="w-full py-3 rounded-xl bg-gradient-to-r from-brand-orange to-brand-purple hover:brightness-110 text-white font-semibold flex items-center justify-center gap-2 transition-all duration-300 disabled:opacity-50"
      >
        <RefreshCw className={`w-4 h-4 ${isAnalyzing ? "animate-spin" : ""}`} />
        <span>{isAnalyzing ? "Re-Ranking Candidates..." : "Re-Rank Candidates"}</span>
      </button>
    </div>
  );
};
