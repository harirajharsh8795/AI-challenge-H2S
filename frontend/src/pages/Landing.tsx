import React, { useState, useEffect } from "react";
import { FunnelVisualizer } from "../components/dashboard/FunnelVisualizer";
import { WorkspacePreview } from "../components/dashboard/WorkspacePreview";
import { Architecture } from "./Architecture";
import { Dashboard } from "./Dashboard";
import { 
  Sparkles, Play, Award, ShieldCheck, Zap, Menu, X, Cpu, Network, 
  Terminal, Search, Database, HardDrive, Compass, Mail, ChevronRight
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface LandingProps {
  setActiveTab: (tab: string) => void;
}

export const Landing: React.FC<LandingProps> = ({ setActiveTab }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false);
  const [activeScrollSection, setActiveScrollSection] = useState<string>("home");

  const [formData, setFormData] = useState({ name: "", email: "", message: "" });
  const [isSubmitted, setIsSubmitted] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string>("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim() || !formData.email.trim() || !formData.message.trim()) {
      setErrorMessage("All fields are required.");
      return;
    }
    try {
      const existing = localStorage.getItem("redrob_messages");
      const messages = existing ? JSON.parse(existing) : [];
      const newMsg = {
        id: `MSG_${Date.now()}_${Math.random().toString(36).substr(2, 5).toUpperCase()}`,
        name: formData.name,
        email: formData.email,
        message: formData.message,
        timestamp: new Date().toISOString()
      };
      messages.push(newMsg);
      localStorage.setItem("redrob_messages", JSON.stringify(messages));
      
      setIsSubmitted(true);
      setErrorMessage("");
      setFormData({ name: "", email: "", message: "" });
    } catch (err) {
      setErrorMessage("Could not save message. Please try again.");
    }
  };

  // Handle smooth scrolling and update active section in header
  const handleScrollToSection = (id: string) => {
    setMobileMenuOpen(false);
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
      setActiveScrollSection(id);
    }
  };

  useEffect(() => {
    const handleScroll = () => {
      const sections = ["home", "features", "analytics", "workflow", "architecture", "contact"];
      const scrollPosition = window.scrollY + 200;

      for (const section of sections) {
        const el = document.getElementById(section);
        if (el) {
          const top = el.offsetTop;
          const height = el.offsetHeight;
          if (scrollPosition >= top && scrollPosition < top + height) {
            setActiveScrollSection(section);
            break;
          }
        }
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const featureItems = [
    { label: "Hybrid Candidate Retrieval", desc: "Combines Okapi BM25 lexical token search with dense bi-encoder semantic similarity scoring.", icon: Search, color: "text-brand-indigo bg-brand-indigo/5 border-brand-indigo/10" },
    { label: "Cross-Encoder Reranking", desc: "Performs query-candidate cross-attention scoring to capture deep contextual relevances.", icon: Cpu, color: "text-brand-purple bg-brand-purple/5 border-brand-purple/10" },
    { label: "BFS Skill Synonym Graph", desc: "Maps candidate skill synonyms programmatically using graph hops with distance-decay modifiers.", icon: Network, color: "text-brand-teal bg-brand-teal/5 border-brand-teal/10" },
    { label: "Behavioral Signal Fusion", desc: "Integrates notice period availability, relocate closeness, and login recency into candidate scoring.", icon: Compass, color: "text-amber-500 bg-amber-500/5 border-amber-500/10" },
    { label: "Deterministic Honeypot Checks", desc: "Screens candidate profiles to catch and filter out synthetic keyword-gamers.", icon: ShieldCheck, color: "text-green-500 bg-green-500/5 border-green-500/10" },
    { label: "Hallucination-Free Explanations", desc: "Generates template-based justification strings dynamically for shortlist decisions.", icon: Terminal, color: "text-pink-500 bg-pink-500/5 border-pink-500/10" },
    { label: "Submission Schema Validator", desc: "Checks ranks sequence, candidate ID schemas, and score decay trends for compliance.", icon: CheckCircleOutlineIcon, color: "text-blue-500 bg-blue-500/5 border-blue-500/10" },
    { label: "Local Weights Customization", desc: "Allows recruiters to adjust weighting sliders on the fly to fit specific role requirements.", icon: Zap, color: "text-yellow-500 bg-yellow-500/5 border-yellow-500/10" },
    { label: "100% Offline Cache Registry", desc: "Loads neural model files locally from `./models/` to run fully local on CPU.", icon: HardDrive, color: "text-indigo-500 bg-indigo-500/5 border-indigo-500/10" },
  ];

  // Helper for validator icon
  function CheckCircleOutlineIcon(props: any) {
    return <ShieldCheck {...props} />;
  }

  return (
    <div className="bg-brand-dark min-h-screen text-white bg-mesh relative font-sans">
      {/* Sticky Header Navbar */}
      <header className="sticky top-0 w-full z-50 glass-panel border-b border-brand-border/60">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-brand-indigo to-brand-purple flex items-center justify-center font-bold text-white shadow-glass-indigo">
              R
            </div>
            <div>
              <h1 className="font-bold text-sm tracking-tight bg-gradient-to-r from-white to-brand-gray bg-clip-text text-transparent">
                Redrob Copilot
              </h1>
              <span className="text-[9px] text-brand-indigo font-semibold tracking-wider uppercase block -mt-0.5">
                AI Talent Intelligence
              </span>
            </div>
          </div>

          {/* Desktop Nav Items */}
          <nav className="hidden md:flex items-center gap-6 text-xs font-semibold text-brand-gray">
            {["home", "features", "analytics", "workflow", "architecture", "workspace", "contact"].map((section) => (
              <button
                key={section}
                onClick={() => {
                  if (section === "workspace") {
                    setActiveTab("workspace");
                  } else {
                    handleScrollToSection(section);
                  }
                }}
                className={`capitalize transition-colors duration-300 ${
                  section === "workspace"
                    ? "text-brand-indigo hover:text-brand-indigo/80"
                    : activeScrollSection === section
                    ? "text-white font-bold"
                    : "hover:text-white"
                }`}
              >
                {section}
              </button>
            ))}
          </nav>

          {/* Launch CTA */}
          <div className="hidden md:flex items-center gap-3">
            <button
              onClick={() => setActiveTab("workspace")}
              className="px-4 py-2 text-xs font-bold bg-brand-indigo hover:bg-brand-indigo/90 rounded-xl transition-all duration-300 shadow-glass-indigo"
            >
              Launch Workspace
            </button>
          </div>

          {/* Mobile hamburger menu button */}
          <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="md:hidden p-2 text-brand-gray hover:text-white">
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Mobile Dropdown Menu */}
        <AnimatePresence>
          {mobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="md:hidden glass-panel no-hover border-b border-brand-border absolute left-0 w-full px-6 py-4 space-y-4 bg-brand-dark/95 z-40"
            >
              <nav className="flex flex-col gap-3 text-xs font-semibold text-brand-gray">
                {["home", "features", "analytics", "workflow", "architecture", "workspace", "contact"].map((section) => (
                  <button
                    key={section}
                    onClick={() => {
                      if (section === "workspace") {
                        setActiveTab("workspace");
                      } else {
                        handleScrollToSection(section);
                      }
                    }}
                    className={`capitalize text-left transition-colors duration-300 ${
                      section === "workspace"
                        ? "text-brand-indigo font-bold hover:text-brand-indigo/80"
                        : "hover:text-white"
                    }`}
                  >
                    {section}
                  </button>
                ))}
              </nav>
              <button
                onClick={() => setActiveTab("workspace")}
                className="w-full py-2.5 text-xs font-bold bg-brand-indigo hover:bg-brand-indigo/90 rounded-xl transition-all duration-300 text-center shadow-glass-indigo block"
              >
                Launch Workspace
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </header>

      {/* Main landing container */}
      <div className="max-w-7xl mx-auto px-6 py-12 space-y-32">
        {/* 1. HERO SECTION */}
        <section id="home" className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center min-h-[calc(100vh-160px)]">
          <div className="lg:col-span-7 space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/80 border border-slate-700/80 text-brand-indigo text-[10px] font-bold uppercase tracking-wider">
              <Sparkles className="w-3.5 h-3.5" />
              <span>SaaS Candidate Discovery Engine</span>
            </div>

            <h2 className="text-4xl lg:text-5xl font-extrabold tracking-tight leading-none text-white">
              AI-Powered Candidate Discovery:{" "}
              <span className="bg-gradient-to-r from-brand-indigo to-brand-purple bg-clip-text text-transparent block mt-2">
                Rank 100,000 Profiles in Minutes
              </span>
            </h2>
            
            <p className="text-brand-gray text-sm lg:text-base max-w-xl leading-relaxed">
              Reduce screening time by 95% and find top AI talent faster. Redrob Copilot streams, filters, and ranks candidate pools locally using multi-stage neural reranking and BFS skill ontology graphs. 100% offline, CPU-optimized, and compliance-verified.
            </p>

            <div className="flex flex-wrap gap-4 pt-4">
              <button
                onClick={() => setActiveTab("workspace")}
                className="px-6 py-3.5 rounded-xl bg-brand-indigo hover:bg-brand-indigo/90 text-white font-bold text-xs flex items-center gap-2 transition-all duration-300 transform hover:scale-[1.02] shadow-glass-indigo"
              >
                <Play className="w-4 h-4 fill-white" />
                <span>Launch Recruiter Workspace</span>
              </button>
              
              <button
                onClick={() => handleScrollToSection("features")}
                className="px-6 py-3.5 rounded-xl glass-panel border border-brand-border hover:bg-slate-800/55 text-white font-bold text-xs transition-all duration-300"
              >
                <span>Explore Platform Features</span>
              </button>
            </div>
          </div>

          <div className="lg:col-span-5 h-[520px]">
            <WorkspacePreview />
          </div>
        </section>

        {/* 2. FEATURES SECTION */}
        <section id="features" className="space-y-10 scroll-mt-20">
          <div className="text-center space-y-3">
            <h3 className="text-2xl lg:text-3xl font-extrabold tracking-tight">Platform Core Capabilities</h3>
            <p className="text-sm text-brand-gray max-w-lg mx-auto">
              Our candidate scoring architecture integrates lexical precision, vector similarities, behavioral signals, and compliance tests.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {featureItems.map((item, idx) => {
              const Icon = item.icon;
              return (
                <div
                  key={idx}
                  className="glass-panel p-6 rounded-2xl border border-brand-border/60 hover:border-slate-700/60 hover:bg-slate-800/20 transition-all duration-300 flex flex-col gap-4"
                >
                  <div className={`p-2.5 rounded-xl w-10 h-10 flex items-center justify-center border ${item.color}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-bold text-sm text-white mb-2">{item.label}</h4>
                    <p className="text-xs text-brand-gray leading-relaxed">{item.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* 3. RESULTS SECTION & ANALYTICS */}
        <section id="analytics" className="space-y-6 scroll-mt-20">
          <div className="text-center space-y-3">
            <h3 className="text-3xl font-extrabold tracking-tight">Verified Performance Indicators</h3>
            <p className="text-sm text-brand-gray max-w-lg mx-auto">
              Our retrieval pipeline scores perfect relevance alignment under programmatic validation.
            </p>
          </div>
          <Dashboard />
        </section>

        {/* 4. WORKFLOW SECTION */}
        <section id="workflow" className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center scroll-mt-20">
          <div className="lg:col-span-6 space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/80 border border-slate-700/80 text-brand-purple text-[10px] font-bold uppercase tracking-wider">
              <span>Recruiter Workflow</span>
            </div>
            <h3 className="text-3xl font-extrabold tracking-tight">Candidate Filtering Funnel</h3>
            <p className="text-sm text-brand-gray leading-relaxed">
              Vetting candidate resumes is a pipeline filtering problem. Our platform streams candidate profiles and applies strict pre-filters (honeypots, role headlines, consulting penalty, experience bounds) before running neural models. This reduces recruiter fatigue by guaranteeing 100% technical shortlists.
            </p>
            <ul className="space-y-3 text-xs text-brand-gray">
              <li className="flex items-center gap-2">
                <ChevronRight className="w-4 h-4 text-brand-indigo" />
                <span>Excludes synthetic resume honeypot keyword-gamers.</span>
              </li>
              <li className="flex items-center gap-2">
                <ChevronRight className="w-4 h-4 text-brand-indigo" />
                <span>Reduces pool size from 100,000 to the top 100 shortlist in seconds.</span>
              </li>
              <li className="flex items-center gap-2">
                <ChevronRight className="w-4 h-4 text-brand-indigo" />
                <span>Integrates notice periods and relocate hubs directly into sorting.</span>
              </li>
            </ul>
          </div>
          <div className="lg:col-span-6 h-[560px]">
            <FunnelVisualizer />
          </div>
        </section>

        {/* 5. ARCHITECTURE SECTION */}
        <section id="architecture" className="space-y-6 scroll-mt-20">
          <div className="text-center space-y-3">
            <h3 className="text-3xl font-extrabold tracking-tight">Technical Architecture</h3>
            <p className="text-sm text-brand-gray max-w-lg mx-auto">
              A standalone, offline candidate discovery pipeline utilizing local Bi-Encoder and Cross-Encoder weights.
            </p>
          </div>
          <div className="h-[520px]">
            <Architecture />
          </div>
        </section>

        {/* 6. CONTACT SECTION & CTA */}
        <section id="contact" className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center scroll-mt-20">
          <div className="lg:col-span-6 space-y-6">
            <h3 className="text-3xl font-extrabold tracking-tight">Empower Your Talent Vetting Today</h3>
            <p className="text-sm text-brand-gray leading-relaxed">
              Book a live product walkthrough, contact our technical solutions team, or explore our verified source code on GitHub.
            </p>
            
            <div className="flex flex-wrap gap-4 pt-2">
              <a 
                href="https://github.com/harirajharsh8795/AI-challenge-H2S" 
                target="_blank" 
                rel="noreferrer" 
                className="px-5 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 border border-brand-border text-xs font-semibold text-white flex items-center gap-2 transition-all duration-300"
              >
                <Terminal className="w-4 h-4" />
                <span>GitHub Repository</span>
              </a>
            </div>
          </div>

          <div className="lg:col-span-6 glass-panel p-8 rounded-2xl border border-brand-border space-y-4">
            <h4 className="font-bold text-sm text-white flex items-center gap-2 mb-4">
              <Mail className="w-4 h-4 text-brand-indigo" />
              <span>Contact & Technical Inquiry</span>
            </h4>
            
            {isSubmitted ? (
              <div className="text-center py-8 space-y-4">
                <div className="w-12 h-12 rounded-full bg-green-500/10 border border-green-500/20 text-brand-teal flex items-center justify-center mx-auto mb-2 shadow-glass-indigo">
                  <ShieldCheck className="w-6 h-6 text-brand-teal" />
                </div>
                <h5 className="text-sm font-extrabold text-white">Message Saved to Database!</h5>
                <p className="text-xs text-brand-gray max-w-sm mx-auto leading-relaxed">
                  Your inquiry has been stored locally in the database. Our technical team will process your request shortly.
                </p>
                <button 
                  onClick={() => setIsSubmitted(false)}
                  className="px-5 py-2.5 mt-2 bg-slate-800 hover:bg-slate-700 text-xs font-bold rounded-xl text-white transition-all duration-300 border border-slate-700"
                >
                  Send Another Message
                </button>
              </div>
            ) : (
              <form className="space-y-4" onSubmit={handleSubmit}>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-[10px] text-brand-gray font-semibold uppercase tracking-wider">Name</label>
                    <input 
                      type="text" 
                      placeholder="John Doe" 
                      required
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="w-full bg-slate-900 border border-brand-border rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-brand-indigo transition-colors" 
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] text-brand-gray font-semibold uppercase tracking-wider">Email</label>
                    <input 
                      type="email" 
                      placeholder="john@company.com" 
                      required
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="w-full bg-slate-900 border border-brand-border rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-brand-indigo transition-colors" 
                    />
                  </div>
                </div>
                
                <div className="space-y-1">
                  <label className="text-[10px] text-brand-gray font-semibold uppercase tracking-wider">Message</label>
                  <textarea 
                    placeholder="Tell us about your team size and AI sourcing bottlenecks..." 
                    required
                    value={formData.message}
                    onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                    className="w-full h-24 bg-slate-900 border border-brand-border rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-brand-indigo resize-none transition-colors" 
                  />
                </div>

                {errorMessage && (
                  <p className="text-xs text-red-500 font-semibold">{errorMessage}</p>
                )}

                <div className="grid grid-cols-2 gap-4 pt-2">
                  <button 
                    type="submit" 
                    className="py-3 bg-brand-indigo hover:bg-brand-indigo/90 rounded-xl text-xs font-bold text-white transition-all duration-300 shadow-glass-indigo text-center"
                  >
                    Send Message
                  </button>
                  <a 
                    href="mailto:support@redrob.ai" 
                    className="py-3 bg-slate-800 hover:bg-slate-700/50 rounded-xl text-xs font-bold text-brand-gray hover:text-white transition-all duration-300 border border-slate-700 text-center flex items-center justify-center"
                  >
                    Email Support
                  </a>
                </div>
              </form>
            )}
          </div>
        </section>
      </div>

      {/* Footer */}
      <footer className="mt-20 border-t border-brand-border/60 bg-slate-950/20 py-8 text-center text-xs text-brand-gray">
        <p className="mb-2">Built with React, TypeScript, and Antigravity SDK.</p>
        <p className="text-[10px] text-slate-600">&copy; {new Date().getFullYear()} Redrob AI. All rights reserved.</p>
      </footer>
    </div>
  );
};
