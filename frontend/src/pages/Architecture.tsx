import React, { useState } from "react";
import { Cpu, ArrowDown, HelpCircle, Network, HardDrive, FileCode } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export const Architecture: React.FC = () => {
  const [selectedNode, setSelectedNode] = useState<number>(1);

  const nodes = [
    {
      id: 1,
      title: "1. Data Stream Ingestion",
      subtitle: "Loader & Memory Streamer",
      desc: "Streams candidate records row-by-row from raw JSONL using generators, keeping the memory footprint under 150MB.",
      input: "data/raw/candidates.jsonl (100,000 rows)",
      output: "Memory Iterator (Streaming dictionaries)",
      model: "Standard Python I/O generators",
      codeFile: "src/data_loader.py",
      codeLine: "L80-L114"
    },
    {
      id: 2,
      title: "2. Hard Pre-Filters",
      subtitle: "Honeypot & Consulting Filters",
      desc: "Disqualifies non-technical roles, consulting-only companies, and synthetic profiles matching 3 honeypot logic rule traps.",
      input: "100,000 Candidate streams",
      output: "6,715 Valid engineering candidates",
      model: "Deterministic checking rules (Title Matcher, Duration check)",
      codeFile: "src/honeypots.py",
      codeLine: "L245-L289"
    },
    {
      id: 3,
      title: "3. Stage 1 Sparse Retrieval",
      subtitle: "Lexical BM25 Search",
      desc: "Computes lexical overlap scores between job description requirements and candidate resume summaries, returning top 2,000 matches.",
      input: "6,715 Clean candidates",
      output: "2,000 Ranked candidates",
      model: "Okapi BM25 (Rank-BM25 library)",
      codeFile: "src/retrieval.py",
      codeLine: "L86-L92"
    },
    {
      id: 4,
      title: "4. Stage 2 Dense Reranking",
      subtitle: "Bi-Encoder Dense Semantic Match",
      desc: "Uses a local, cached bi-encoder model to encode JD and candidates into 384-dimensional dense vectors, returning the top 500 by Cosine Similarity.",
      input: "2,000 Candidates",
      output: "500 Reranked candidates",
      model: "all-MiniLM-L6-v2 (sentence-transformers)",
      codeFile: "src/semantic_reranker.py",
      codeLine: "L62-L64"
    },
    {
      id: 5,
      title: "5. Stage 3 Contextual Reranking",
      subtitle: "Cross-Encoder Attention Match",
      desc: "Applies deep query-document cross-attention models over the top 150 candidates, capturing contextual intent and synonym matching.",
      input: "150 Candidates",
      output: "150 Blended reranked candidates",
      model: "ms-marco-MiniLM-L-6-v2 (sentence-transformers)",
      codeFile: "src/cross_encoder_reranker.py",
      codeLine: "L64-L66"
    },
    {
      id: 6,
      title: "6. Stage 4 Behavioral scoring",
      subtitle: "Composite Weights Signal Fusion",
      desc: "Blends semantic scores with simulated platform signals: Relocation locations, response rate, notice period, and login recency multipliers.",
      input: "150 Candidates",
      output: "100 Shortlisted candidates",
      model: "Composite Fusion scoring formula",
      codeFile: "src/behavioral_scoring.py",
      codeLine: "L337-L350"
    },
    {
      id: 7,
      title: "7. Explainability & Output",
      subtitle: "Hallucination-free templates",
      desc: "Dynamically compiles factual, template-styled explanation summaries for each candidate and writes ranks to a schema-conforming CSV.",
      input: "100 Scored candidates",
      output: "data/processed/submission.csv (100 rows)",
      model: "Deterministic templates & compliance validator",
      codeFile: "src/explainability.py",
      codeLine: "L15-L50"
    }
  ];

  const activeNode = nodes.find((n) => n.id === selectedNode) || nodes[0];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 pb-12 h-auto lg:h-[calc(100vh-150px)] lg:overflow-hidden">
      {/* LEFT COLUMN: Pipeline flowchart */}
      <div className="lg:col-span-6 glass-panel p-6 rounded-2xl border border-brand-border flex flex-col h-auto lg:h-full overflow-visible lg:overflow-hidden">
        <div className="flex items-center gap-2 border-b border-brand-border pb-4 mb-6">
          <Network className="w-5 h-5 text-brand-purple" />
          <h3 className="font-bold text-sm text-white">Interactive Processing Stages</h3>
        </div>

        {/* Nodes flow list */}
        <div className="space-y-2 pr-2 lg:flex-1 lg:overflow-y-auto">
          {nodes.map((node) => {
            const isActive = selectedNode === node.id;
            return (
              <React.Fragment key={node.id}>
                <motion.div
                  onMouseEnter={() => setSelectedNode(node.id)}
                  onClick={() => setSelectedNode(node.id)}
                  whileHover={{ scale: 1.025 }}
                  animate={{ 
                    scale: isActive ? 1.025 : 1.0,
                    borderColor: isActive ? "#6366F1" : "rgba(30, 41, 59, 0.6)",
                    backgroundColor: isActive ? "rgba(99, 102, 241, 0.15)" : "rgba(14, 21, 36, 0.4)"
                  }}
                  transition={{ duration: 0.18 }}
                  className={`p-3.5 rounded-xl border cursor-pointer flex items-center justify-between transition-shadow ${
                    isActive ? "shadow-[0_0_15px_rgba(99,102,241,0.2)]" : ""
                  }`}
                >
                  <div className="min-w-0">
                    <span className={`text-[10px] font-bold block ${isActive ? "text-brand-purple" : "text-brand-gray"}`}>
                      {node.subtitle}
                    </span>
                    <span className="font-bold text-xs text-white block mt-0.5 truncate">
                      {node.title}
                    </span>
                  </div>
                  <span className="text-[10px] bg-slate-800 border border-slate-700 text-brand-gray px-2 py-0.5 rounded font-mono">
                    {node.codeFile.split("/")[1]}
                  </span>
                </motion.div>
                {node.id < nodes.length && (
                  <div className="flex justify-center my-0.5">
                    <ArrowDown className="w-3.5 h-3.5 text-slate-700" />
                  </div>
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* RIGHT COLUMN: Node Detail Inspector */}
      <div className="lg:col-span-6 glass-panel p-6 rounded-2xl border border-brand-border flex flex-col h-auto lg:h-full overflow-visible lg:overflow-hidden bg-[#04060b]">
        <div className="flex items-center gap-2 border-b border-brand-border pb-4 mb-6">
          <Cpu className="w-5 h-5 text-brand-indigo" />
          <h3 className="font-bold text-sm text-white">Technical Details Inspector</h3>
        </div>

        {/* Node details wrapper with AnimatePresence */}
        <div className="lg:flex-1 lg:overflow-hidden lg:relative min-h-[360px] lg:min-h-0">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeNode.id}
              initial={{ opacity: 0, x: 12 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -12 }}
              transition={{ duration: 0.2 }}
              className="space-y-6 pr-2 h-auto lg:absolute lg:inset-0 lg:overflow-y-auto"
            >
              <div>
                <span className="text-[10px] text-brand-indigo font-bold uppercase tracking-wider block">
                  {activeNode.subtitle}
                </span>
                <h4 className="text-xl font-extrabold text-white mt-1">
                  {activeNode.title}
                </h4>
                <p className="text-xs text-brand-gray mt-3 leading-relaxed">
                  {activeNode.desc}
                </p>
              </div>

              <div className="space-y-4 pt-4 border-t border-brand-border/60">
                {/* Input Data */}
                <div className="grid grid-cols-3 gap-2 text-xs">
                  <span className="text-slate-500 font-semibold uppercase tracking-wider text-[9px] mt-0.5">Input Scope</span>
                  <span className="col-span-2 text-slate-300 font-medium">{activeNode.input}</span>
                </div>

                {/* Output Data */}
                <div className="grid grid-cols-3 gap-2 text-xs">
                  <span className="text-slate-500 font-semibold uppercase tracking-wider text-[9px] mt-0.5">Output Scope</span>
                  <span className="col-span-2 text-slate-300 font-medium">{activeNode.output}</span>
                </div>

                {/* Algorithm / Model */}
                <div className="grid grid-cols-3 gap-2 text-xs">
                  <span className="text-slate-500 font-semibold uppercase tracking-wider text-[9px] mt-0.5">Model / Engine</span>
                  <span className="col-span-2 text-slate-300 font-semibold text-brand-purple">{activeNode.model}</span>
                </div>

                {/* Code Reference link */}
                <div className="grid grid-cols-3 gap-2 text-xs items-center pt-2">
                  <span className="text-slate-500 font-semibold uppercase tracking-wider text-[9px]">Source Code</span>
                  <a
                    href={`file:///e:/Desktop/H2S REDROB/India_runs_data_and_ai_challenge/${activeNode.codeFile}#${activeNode.codeLine}`}
                    target="_blank"
                    rel="noreferrer"
                    className="col-span-2 inline-flex items-center gap-1.5 text-brand-indigo hover:underline font-semibold font-mono text-[11px]"
                  >
                    <FileCode className="w-3.5 h-3.5" />
                    <span>{activeNode.codeFile}:{activeNode.codeLine}</span>
                  </a>
                </div>
              </div>

              {/* Sandbox Info */}
              <div className="p-4 rounded-xl bg-slate-900/40 border border-brand-border flex items-start gap-3 mt-6">
                <HardDrive className="w-5 h-5 text-brand-teal flex-shrink-0 mt-0.5" />
                <div>
                  <span className="text-[10px] text-brand-teal font-semibold uppercase tracking-wider block">
                    Offline Execution Spec
                  </span>
                  <span className="text-[10px] text-slate-400 block mt-1 leading-normal">
                    Models are fetched locally from weights stored under the <span className="text-white font-semibold">./models/</span> directory, completely avoiding external API load times and enabling offline execution.
                  </span>
                </div>
              </div>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};
