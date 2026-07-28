import React, { useState } from "react";
import { BookOpen, Search, FileText, ExternalLink, Hash } from "lucide-react";

export const KnowledgePage: React.FC = () => {
  const [search, setSearch] = useState("");

  const runbooks = [
    { id: "RB-42", title: "Demographic Covariate Slice Retraining Protocol", category: "Feature Drift", vectors: 142, lastModified: "3 days ago", snippet: "When Wasserstein distance surges above 0.10 on demographic inputs, rollback preprocessing to stable release and apply dynamic slice filtering before triggering retraining." },
    { id: "RB-18", title: "OpenTelemetry P99 Latency Cache Miss Mitigation", category: "Latency Degradation", vectors: 88, lastModified: "1 week ago", snippet: "Verify online embedding table lookup memory utilization. If covariate drift occurs simultaneously, defer infrastructure scaling and execute model recalibration." },
    { id: "RB-09", title: "LLM Hallucination & Prompt Guard Override", category: "Generative AI", vectors: 204, lastModified: "2 days ago", snippet: "When semantic perplexity score exceeds safety boundary, restrict generative sampling temperature to 0.2 and enable strict output schema validation." },
  ];

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6 font-sans">
      <div className="flex items-center justify-between border-b border-border pb-4">
        <div>
          <h2 className="text-lg font-bold text-slate-100">Vector Runbook Knowledge Base</h2>
          <p className="text-xs text-slate-400 mt-1">Indexed operational guidelines automatically retrieved by Probe during causal hypothesis reasoning.</p>
        </div>
        <div className="w-80 relative font-mono text-xs">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search runbook semantic vectors..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded pl-8 pr-3 py-1.5 text-slate-200 focus:outline-none focus:border-slate-600 font-sans"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {runbooks.map((rb) => (
          <div key={rb.id} className="bg-card border border-border rounded-md p-5 space-y-3 hover:border-slate-600 transition-colors">
            <div className="flex items-center justify-between font-mono text-xs">
              <div className="flex items-center space-x-2">
                <span className="px-2 py-0.5 bg-blue-950 text-blue-300 border border-blue-800 font-bold rounded">
                  {rb.id}
                </span>
                <span className="font-bold text-sm text-slate-100 font-sans">{rb.title}</span>
              </div>
              <span className="text-slate-400">Category: {rb.category}</span>
            </div>
            <p className="text-xs text-slate-300 font-sans leading-relaxed">{rb.snippet}</p>
            <div className="pt-2 border-t border-slate-900 flex justify-between items-center text-[11px] text-slate-400 font-mono">
              <span className="flex items-center gap-1.5"><Hash className="w-3 h-3 text-blue-400" /> Indexed Vectors: {rb.vectors} embeddings</span>
              <span>Updated {rb.lastModified}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
