import React, { useState } from "react";
import { Sidebar } from "./components/layout/Sidebar";
import { Landing } from "./pages/Landing";
import { Demo } from "./pages/Demo";
import { Dashboard } from "./pages/Dashboard";
import { Validator } from "./pages/Validator";
import { Architecture } from "./pages/Architecture";
import { Activity } from "lucide-react";

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>("landing");

  const renderWorkspaceContent = () => {
    switch (activeTab) {
      case "workspace":
        return <Demo />;
      case "analytics":
        return <Dashboard />;
      case "validator":
        return <Validator />;
      case "architecture":
        return <Architecture />;
      default:
        return <Demo />;
    }
  };

  // 1. Landing Page Mode (Public Marketing Page - Full Width)
  if (activeTab === "landing") {
    return <Landing setActiveTab={setActiveTab} />;
  }

  // 2. Recruiter Workspace Console Mode (Left Sidebar Layout)
  return (
    <div className="min-h-screen bg-mesh bg-brand-dark flex select-none">
      {/* Navigation Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Pane */}
      <main className="flex-1 pl-72 py-8 min-w-0">
        <header className="flex items-center justify-between pr-6 mb-8 border-b border-brand-border/40 pb-5">
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight">
              {activeTab === "workspace" && "Candidate Discovery Workspace"}
              {activeTab === "analytics" && "Search Quality & Performance"}
              {activeTab === "validator" && "Compliance Validation Center"}
              {activeTab === "architecture" && "Pipeline Architecture Blueprint"}
            </h2>
            <p className="text-xs text-brand-gray mt-1">
              {activeTab === "workspace" && "Configure priority weights, edit requirements, and review candidate profile intelligence."}
              {activeTab === "analytics" && "Review search accuracy curves, indexing throughput, and CPU/RAM execution footprints."}
              {activeTab === "validator" && "Monitor automated pipeline unit testing suites and schema validator logs."}
              {activeTab === "architecture" && "Inspect local models caching registry and step-by-step pipeline blueprint configurations."}
            </p>
          </div>

          <div className="flex items-center gap-2 text-xs font-semibold px-3 py-1.5 rounded-full bg-slate-900 border border-brand-border text-brand-teal">
            <Activity className="w-3.5 h-3.5 animate-pulse" />
            <span>Talent Engine: Local CPU Mode</span>
          </div>
        </header>

        {/* Dynamic workspace panels */}
        <div className="min-h-[calc(100vh-140px)] flex flex-col pr-6">
          {renderWorkspaceContent()}
        </div>
      </main>
    </div>
  );
};

export default App;
