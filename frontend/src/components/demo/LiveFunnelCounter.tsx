import React, { useEffect, useState } from "react";
import { StatsAPI } from "../../api";

interface LiveFunnelCounterProps {
  stats: StatsAPI | null;
}

export const LiveFunnelCounter: React.FC<LiveFunnelCounterProps> = ({ stats }) => {
  const [profiles, setProfiles] = useState(0);
  const [seconds, setSeconds] = useState(0);
  const [shortlist, setShortlist] = useState(0);
  const [ram, setRam] = useState(0);

  // Targets from stats prop
  const targetProfiles = stats?.total_ingested ?? 100000;
  const targetSeconds = stats?.runtime_seconds ?? 193.94;
  const targetShortlist = stats?.final_shortlist ?? 100;
  const targetRam = stats?.peak_memory_mb ?? 128;

  useEffect(() => {
    const duration = 2000; // 2 seconds
    const start = performance.now();

    const animate = (now: number) => {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function (easeOutQuad)
      const ease = progress * (2 - progress);

      setProfiles(Math.floor(ease * targetProfiles));
      setSeconds(parseFloat((ease * targetSeconds).toFixed(2)));
      setShortlist(Math.floor(ease * targetShortlist));
      setRam(Math.floor(ease * targetRam));

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }, [stats, targetProfiles, targetSeconds, targetShortlist, targetRam]);

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 w-full mb-6">
      <div className="glass-panel p-5 rounded-2xl border border-brand-border/60 hover:border-brand-purple/30 transition-all duration-300 bg-slate-900/40 text-center">
        <span className="text-[10px] text-brand-gray uppercase tracking-wider font-extrabold block">Profiles Analyzed</span>
        <span className="text-3xl font-black text-white mt-1 block tracking-tight">
          {profiles.toLocaleString()}
        </span>
      </div>
      <div className="glass-panel p-5 rounded-2xl border border-brand-border/60 hover:border-brand-indigo/30 transition-all duration-300 bg-slate-900/40 text-center">
        <span className="text-[10px] text-brand-gray uppercase tracking-wider font-extrabold block">Execution Time</span>
        <span className="text-3xl font-black text-sky-400 mt-1 block tracking-tight">
          {seconds.toFixed(2)}s
        </span>
      </div>
      <div className="glass-panel p-5 rounded-2xl border border-brand-border/60 hover:border-brand-teal/30 transition-all duration-300 bg-slate-900/40 text-center">
        <span className="text-[10px] text-brand-gray uppercase tracking-wider font-extrabold block">Shortlisted Candidates</span>
        <span className="text-3xl font-black text-brand-teal mt-1 block tracking-tight">
          {shortlist}
        </span>
      </div>
      <div className="glass-panel p-5 rounded-2xl border border-brand-border/60 hover:border-rose-500/30 transition-all duration-300 bg-slate-900/40 text-center">
        <span className="text-[10px] text-brand-gray uppercase tracking-wider font-extrabold block">Peak RAM Usage</span>
        <span className="text-3xl font-black text-rose-500 mt-1 block tracking-tight font-mono">
          &lt; {ram} MB
        </span>
      </div>
    </div>
  );
};
