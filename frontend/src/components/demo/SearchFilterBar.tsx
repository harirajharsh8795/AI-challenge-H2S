import React, { useState } from "react";
import { Search, SlidersHorizontal } from "lucide-react";

interface SearchFilterBarProps {
  onFilterChange: (filters: { search: string; notice: string; minScore: number }) => void;
}

export const SearchFilterBar: React.FC<SearchFilterBarProps> = ({ onFilterChange }) => {
  const [search, setSearch] = useState("");
  const [notice, setNotice] = useState("all");
  const [minScore, setMinScore] = useState(0.95);

  const handleSearchChange = (val: string) => {
    setSearch(val);
    onFilterChange({ search: val, notice, minScore });
  };

  const handleNoticeChange = (val: string) => {
    setNotice(val);
    onFilterChange({ search, notice: val, minScore });
  };

  const handleScoreChange = (val: number) => {
    setMinScore(val);
    onFilterChange({ search, notice, minScore: val });
  };

  return (
    <div className="glass-panel p-5 rounded-2xl border border-brand-border/60 bg-slate-900/40 mb-6 w-full flex flex-col md:flex-row items-center gap-4">
      {/* Skill search */}
      <div className="relative w-full md:flex-1">
        <Search className="w-4 h-4 text-brand-gray absolute left-3.5 top-1/2 -translate-y-1/2" />
        <input 
          type="text"
          placeholder="Filter by skill synonym (e.g. Python, Lora, Bm25, Qlora, Peft)..."
          value={search}
          onChange={(e) => handleSearchChange(e.target.value)}
          className="w-full bg-slate-950 border border-brand-border rounded-xl pl-10 pr-4 py-2.5 text-xs text-white placeholder-brand-gray focus:outline-none focus:border-brand-purple transition-all"
        />
      </div>

      {/* Notice dropdown */}
      <div className="w-full md:w-56">
        <select
          value={notice}
          onChange={(e) => handleNoticeChange(e.target.value)}
          className="w-full bg-slate-950 border border-brand-border rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-brand-purple cursor-pointer"
        >
          <option value="all">All Notice Periods</option>
          <option value="0">Immediate Joiner (0 days)</option>
          <option value="30">Within 30 Days</option>
          <option value="90">90 Days Notice</option>
        </select>
      </div>

      {/* Score slider */}
      <div className="w-full md:w-72 flex items-center gap-3 bg-slate-950 border border-brand-border rounded-xl px-4 py-2 text-xs">
        <SlidersHorizontal className="w-4 h-4 text-brand-gray flex-shrink-0" />
        <div className="flex-1 space-y-0.5">
          <div className="flex justify-between text-[10px] text-brand-gray">
            <span>Minimum Fused Score</span>
            <span className="font-extrabold text-brand-indigo">{minScore.toFixed(3)}</span>
          </div>
          <input 
            type="range" 
            min="0.950" 
            max="1.060" 
            step="0.005"
            value={minScore}
            onChange={(e) => handleScoreChange(parseFloat(e.target.value))}
            className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500 focus:outline-none"
          />
        </div>
      </div>
    </div>
  );
};
