import React from "react";
import { Users, BarChart3, CheckCircle2, Cpu, LogOut, Shield } from "lucide-react";

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const menuItems = [
    { id: "workspace", label: "Talent Search Workspace", icon: Users },
    { id: "analytics", label: "Search Quality Analytics", icon: BarChart3 },
    { id: "validator", label: "Validation Center", icon: CheckCircle2 },
    { id: "architecture", label: "Pipeline Architecture", icon: Cpu },
  ];

  return (
    <aside className="w-64 glass-panel border-r border-brand-border h-screen flex flex-col fixed left-0 top-0 z-30">
      {/* Brand Header */}
      <div className="p-6 border-b border-brand-border flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-brand-orange to-brand-purple flex items-center justify-center font-bold text-white shadow-glass-orange">
          R
        </div>
        <div>
          <h1 className="font-bold text-sm tracking-tight bg-gradient-to-r from-white to-brand-gray bg-clip-text text-transparent">
            Redrob Copilot
          </h1>
          <span className="text-[10px] text-brand-orange font-semibold tracking-wider uppercase">
            Candidate Discovery
          </span>
        </div>
      </div>

      {/* Navigation list */}
      <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 font-medium text-xs group ${
                isActive
                  ? "bg-brand-orange text-white shadow-glass-orange font-semibold"
                  : "text-brand-gray hover:text-white hover:bg-slate-800/50"
              }`}
            >
              <Icon
                className={`w-4 h-4 transition-transform duration-300 group-hover:scale-110 ${
                  isActive ? "text-white" : "text-brand-gray group-hover:text-brand-orange"
                }`}
              />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Return to marketing page button */}
      <div className="px-4 py-3 border-t border-brand-border">
        <button
          onClick={() => setActiveTab("landing")}
          className="w-full flex items-center gap-2 px-4 py-2.5 rounded-lg text-brand-gray hover:text-white hover:bg-red-500/10 hover:text-red-400 transition-all duration-300 font-semibold text-xs"
        >
          <LogOut className="w-4 h-4" />
          <span>Exit Workspace</span>
        </button>
      </div>

      {/* Footer Info */}
      <div className="p-4 bg-slate-900/30 border-t border-brand-border">
        <div className="flex items-center justify-between text-[10px] text-brand-gray">
          <span>Engine Status:</span>
          <span className="flex items-center gap-1 font-semibold text-brand-teal">
            <span className="w-1.5 h-1.5 rounded-full bg-brand-teal animate-pulse" />
            Verified Offline
          </span>
        </div>
      </div>
    </aside>
  );
};
