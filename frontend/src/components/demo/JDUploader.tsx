import React from "react";
import { FileText, MapPin, Calendar, CheckSquare } from "lucide-react";
import { usePipeline } from "../../context/PipelineContext";
import { extractedRequirements } from "../../utils/mockData";

export const JDUploader: React.FC = () => {
  const { jdText } = usePipeline();

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 border-b border-brand-border pb-4">
        <FileText className="w-4 h-4 text-brand-indigo" />
        <h4 className="font-bold text-sm">Extracted Role Specifications</h4>
      </div>

      <div className="space-y-4">
        {/* Experience Bounds */}
        <div className="flex items-start gap-3 p-3 rounded-xl bg-slate-800/30 border border-brand-border">
          <Calendar className="w-4 h-4 text-brand-teal mt-0.5" />
          <div>
            <span className="text-[10px] text-brand-gray block font-semibold uppercase tracking-wider">
              Experience Scope
            </span>
            <span className="text-xs font-semibold text-white">
              Target: {extractedRequirements.min_experience}-{extractedRequirements.max_experience} Years
            </span>
            <span className="text-[10px] text-slate-500 block">
              Hard filter: 3-12 Years
            </span>
          </div>
        </div>

        {/* Location Hubs */}
        <div className="flex items-start gap-3 p-3 rounded-xl bg-slate-800/30 border border-brand-border">
          <MapPin className="w-4 h-4 text-brand-purple mt-0.5" />
          <div>
            <span className="text-[10px] text-brand-gray block font-semibold uppercase tracking-wider">
              Location Hubs
            </span>
            <div className="flex flex-wrap gap-1.5 mt-1">
              {extractedRequirements.locations.map((loc) => (
                <span
                  key={loc}
                  className="text-[9px] bg-slate-800 border border-slate-700 text-brand-gray px-1.5 py-0.5 rounded"
                >
                  {loc}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Must-Have Skills */}
        <div className="flex items-start gap-3 p-3 rounded-xl bg-slate-800/30 border border-brand-border">
          <CheckSquare className="w-4 h-4 text-brand-indigo mt-0.5" />
          <div>
            <span className="text-[10px] text-brand-gray block font-semibold uppercase tracking-wider">
              Must-Have Technical Skills
            </span>
            <div className="flex flex-wrap gap-1 mt-1">
              {extractedRequirements.must_have.map((skill) => (
                <span
                  key={skill}
                  className="text-[9px] bg-slate-800 text-white px-2 py-0.5 rounded border border-slate-700/80 font-medium"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="space-y-1">
        <span className="text-[10px] text-brand-gray block font-semibold uppercase tracking-wider">
          Job Description Text
        </span>
        <textarea
          readOnly
          value={jdText}
          className="w-full h-32 bg-slate-900 border border-brand-border rounded-xl p-3 text-[11px] text-slate-400 font-mono focus:outline-none resize-none"
        />
      </div>
    </div>
  );
};
