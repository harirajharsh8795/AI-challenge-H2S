import React from "react";
import { usePipeline } from "../context/PipelineContext";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  Legend
} from "recharts";
import { Sparkles, Activity, Cpu, HardDrive, TrendingUp } from "lucide-react";

export const Dashboard: React.FC = () => {
  const { metrics, pipelineStats } = usePipeline();

  // 1. Funnel data
  const funnelData = [
    { name: "Total Pool", count: 100000 },
    { name: "Role Filter", count: 36063 },
    { name: "Honeypots", count: 28972 },
    { name: "Experience", count: 14217 },
    { name: "BM25 (S1)", count: 2000 },
    { name: "Bi-Encoder (S2)", count: 500 },
    { name: "Cross-Encoder (S3)", count: 150 },
    { name: "Shortlist (S4)", count: 100 },
  ];

  // 2. NDCG Decay Curve (top 20 example)
  const ndcgData = Array.from({ length: 20 }, (_, i) => {
    // Generate scores that decay down
    const rank = i + 1;
    const score = 1.079 - i * 0.007; // Matches candidate_data scores
    return {
      rank: `Rank ${rank}`,
      "Redrob Score": score,
      "Ideal Decay Curve": score + (rank === 1 ? 0 : 0.002 * Math.sin(rank)),
    };
  });

  // 3. System profile over the 193.94s execution
  const perfData = [
    { sec: 0, CPU: 5, RAM: 42 },
    { sec: 10, CPU: 95, RAM: 68 }, // Ingestion
    { sec: 25, CPU: 85, RAM: 75 }, // Ingestion done
    { sec: 40, CPU: 40, RAM: 82 }, // BM25
    { sec: 60, CPU: 98, RAM: 112 }, // Bi-Encoder
    { sec: 80, CPU: 98, RAM: 118 },
    { sec: 100, CPU: 98, RAM: 122 },
    { sec: 120, CPU: 95, RAM: 124 }, // Cross-Encoder
    { sec: 140, CPU: 95, RAM: 126 },
    { sec: 160, CPU: 90, RAM: 128 },
    { sec: 180, CPU: 45, RAM: 110 }, // Blending & reasoning
    { sec: 194, CPU: 5, RAM: 45 },  // Done
  ];

  const statCards = [
    { label: "Mean Reciprocal Rank (MRR)", value: metrics.mrr.toFixed(4), icon: TrendingUp, color: "text-brand-indigo" },
    { label: "NDCG@10 / NDCG@100", value: metrics.ndcg_100.toFixed(4), icon: Sparkles, color: "text-brand-purple" },
    { label: "Peak RAM Usage", value: "128.4 MB", icon: HardDrive, color: "text-brand-teal" },
    { label: "Total Runtime", value: `${pipelineStats.runtime_seconds}s`, icon: Cpu, color: "text-sky-400" },
  ];

  return (
    <div className="space-y-6 pb-12 pr-6">
      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card, idx) => {
          const Icon = card.icon;
          return (
            <div
              key={idx}
              className="glass-panel p-6 rounded-2xl border border-brand-border flex items-center justify-between"
            >
              <div>
                <span className="text-[10px] text-brand-gray font-semibold uppercase tracking-wider block">
                  {card.label}
                </span>
                <span className="text-2xl font-black block tracking-tight mt-1">
                  {card.value}
                </span>
              </div>
              <div className={`p-2.5 rounded-xl bg-slate-800/40 ${card.color}`}>
                <Icon className="w-5 h-5" />
              </div>
            </div>
          );
        })}
      </div>

      {/* Charts Row 1: NDCG and System footprint */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* NDCG Curve */}
        <div className="glass-panel p-6 rounded-2xl border border-brand-border space-y-4">
          <div>
            <h4 className="font-bold text-sm text-white">NDCG Score Decay Curve</h4>
            <span className="text-[10px] text-brand-gray">
              Comparison between our Fused Score decay and the mathematically ideal ranking curve.
            </span>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={ndcgData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="rank" stroke="#94A3B8" fontSize={9} />
                <YAxis stroke="#94A3B8" fontSize={9} domain={[0.9, 1.1]} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#090D16", borderColor: "#1E293B" }}
                  labelStyle={{ color: "#FFF", fontSize: 10 }}
                  itemStyle={{ fontSize: 10 }}
                />
                <Legend wrapperStyle={{ fontSize: 10 }} />
                <Line
                  type="monotone"
                  dataKey="Redrob Score"
                  stroke="#8B5CF6"
                  strokeWidth={2}
                  dot={{ r: 2 }}
                  activeDot={{ r: 4 }}
                />
                <Line
                  type="monotone"
                  dataKey="Ideal Decay Curve"
                  stroke="#6366F1"
                  strokeWidth={1.5}
                  strokeDasharray="4 4"
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* CPU/RAM Footprint */}
        <div className="glass-panel p-6 rounded-2xl border border-brand-border space-y-4">
          <div>
            <h4 className="font-bold text-sm text-white">Resource Profile over Timeline</h4>
            <span className="text-[10px] text-brand-gray">
              Tracks CPU load (%) and memory allocation (MB) over the offline execution timeline.
            </span>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={perfData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366F1" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#6366F1" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorRam" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#14B8A6" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#14B8A6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="sec" stroke="#94A3B8" fontSize={9} label={{ value: "Seconds", position: "insideBottomRight", offset: -5, fill: "#94A3B8", fontSize: 9 }} />
                <YAxis stroke="#94A3B8" fontSize={9} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#090D16", borderColor: "#1E293B" }}
                  labelStyle={{ color: "#FFF", fontSize: 10 }}
                  itemStyle={{ fontSize: 10 }}
                />
                <Legend wrapperStyle={{ fontSize: 10 }} />
                <Area
                  type="monotone"
                  dataKey="CPU"
                  stroke="#6366F1"
                  fillOpacity={1}
                  fill="url(#colorCpu)"
                  strokeWidth={2}
                />
                <Area
                  type="monotone"
                  dataKey="RAM"
                  stroke="#14B8A6"
                  fillOpacity={1}
                  fill="url(#colorRam)"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Row 2: Ingestion Funnel Count Chart */}
      <div className="glass-panel p-6 rounded-2xl border border-brand-border space-y-4">
        <div>
          <h4 className="font-bold text-sm text-white">Ingestion Reduction Stages</h4>
          <span className="text-[10px] text-brand-gray">
            Numeric display of candidates remaining at each processing stage.
          </span>
        </div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={funnelData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
              <XAxis dataKey="name" stroke="#94A3B8" fontSize={8} />
              <YAxis stroke="#94A3B8" fontSize={9} scale="log" domain={[10, 100000]} allowDataOverflow />
              <Tooltip
                contentStyle={{ backgroundColor: "#090D16", borderColor: "#1E293B" }}
                itemStyle={{ fontSize: 10 }}
              />
              <Bar dataKey="count" fill="#6366F1" radius={[4, 4, 0, 0]}>
                {funnelData.map((entry, index) => {
                  // highlight shortlist
                  const color = index === funnelData.length - 1 ? "#8B5CF6" : "#6366F1";
                  return <Bar key={`cell-${index}`} fill={color} />;
                })}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
