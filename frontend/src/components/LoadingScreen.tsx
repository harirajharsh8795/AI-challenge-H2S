import React, { useEffect, useState } from "react";

const steps = [
  "Initializing Redrob Copilot...",
  "Loading 1,00,000 candidate profiles...",
  "Running BM25 + Bi-Encoder + Cross-Encoder pipeline...",
  "Shortlist ready. 100 candidates ranked.",
];

const progressValues = [10, 40, 80, 100];

export const LoadingScreen: React.FC<{ onComplete: () => void }> = ({ onComplete }) => {
  const [step, setStep] = useState(0);
  const [progress, setProgress] = useState(0);
  const [fading, setFading] = useState(false);

  useEffect(() => {
    const timers: ReturnType<typeof setTimeout>[] = [];
    steps.forEach((_, i) => {
      timers.push(setTimeout(() => {
        setStep(i);
        setProgress(progressValues[i]);
      }, i * 600));
    });
    timers.push(setTimeout(() => setFading(true), 2600));
    timers.push(setTimeout(() => onComplete(), 3000));
    return () => timers.forEach(clearTimeout);
  }, [onComplete]);

  return (
    <div className={`fixed inset-0 z-50 flex flex-col items-center justify-center bg-[#0f0f1a] transition-all duration-400 ${
      fading ? "opacity-0 scale-105 pointer-events-none" : "opacity-100 scale-100"
    }`}>
      
      {/* Logo */}
      <div className="mb-12 text-center">
        <span className="text-2xl font-black text-white tracking-tight">
          Redrob <span className="text-[#6366f1]">Copilot</span>
        </span>
        <p className="text-xs text-slate-500 mt-1 font-medium">AI Talent Intelligence Platform</p>
      </div>

      {/* Spinner + Step text */}
      <div className="flex items-center gap-3 mb-8">
        <div className="w-4 h-4 border-2 border-[#6366f1] border-t-transparent rounded-full animate-spin" />
        <span className="text-sm text-slate-300 font-mono transition-all duration-300">
          {steps[step]}
        </span>
      </div>

      {/* Progress bar */}
      <div className="w-80 h-1.5 bg-slate-800 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500 ease-out"
          style={{
            width: `${progress}%`,
            background: "linear-gradient(90deg, #6366f1, #22c55e)",
          }}
        />
      </div>
      <span className="text-[10px] text-slate-600 mt-2 font-mono">{progress}%</span>

      {/* Bottom badge */}
      <div className="absolute bottom-8 text-[10px] text-slate-600 font-medium">
        Powered by Google Antigravity SDK • Gemini 1.5 Flash
      </div>
    </div>
  );
};
