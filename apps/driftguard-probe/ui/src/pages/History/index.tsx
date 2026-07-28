import React from "react";
import { History, Calendar, ShieldCheck, Download, ExternalLink } from "lucide-react";

export const HistoryPage: React.FC = () => {
  const archives = [
    { id: "inc-checkout-latency-104", date: "July 26, 2026", model: "payment-routing-v3", resolution: "Retraining pipeline completed successfully", author: "Intervention Architect", duration: "3m 12s", confidence: 94 },
    { id: "inc-llm-hallucination-42", date: "July 25, 2026", model: "gpt-4-summarizer", resolution: "Updated system prompt semantic filtering rules", author: "SRE Executive Override", duration: "5m 22s", confidence: 91 },
    { id: "inc-drift-batch-88", date: "July 24, 2026", model: "churn-propensity-v1", resolution: "Automated threshold recalibration dispatched", author: "System Automated", duration: "2m 50s", confidence: 89 },
  ];

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6 font-sans">
      <div className="border-b border-border pb-4">
        <h2 className="text-lg font-bold text-slate-100">Historical Investigation Ledger</h2>
        <p className="text-xs text-slate-400 mt-1">Immutable time-travel replay journals and completed anomaly diagnostic post-mortems.</p>
      </div>

      <div className="border border-border bg-card rounded-md divide-y divide-border font-mono text-xs">
        {archives.map((rec) => (
          <div key={rec.id} className="p-4 flex items-center justify-between hover:bg-slate-900/40 transition-colors">
            <div className="space-y-1 font-sans">
              <div className="flex items-center space-x-2 font-mono">
                <History className="w-4 h-4 text-blue-400" />
                <span className="font-bold text-blue-400">{rec.id}</span>
                <span className="text-slate-400">({rec.model})</span>
              </div>
              <p className="text-slate-300 font-medium">{rec.resolution}</p>
              <div className="flex items-center space-x-4 text-[11px] text-slate-400 font-mono pt-1">
                <span>Date: {rec.date}</span>
                <span>|</span>
                <span>Author: {rec.author}</span>
                <span>|</span>
                <span className="text-emerald-400 flex items-center gap-1"><ShieldCheck className="w-3.5 h-3.5" /> Confidence: {rec.confidence}%</span>
              </div>
            </div>

            <div className="flex items-center space-x-2 shrink-0 font-sans">
              <button className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 rounded text-xs font-semibold flex items-center gap-1.5 transition-colors">
                <Download className="w-3.5 h-3.5 text-slate-400" /> Export CQRS Journal
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
