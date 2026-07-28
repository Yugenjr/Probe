import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Clock, CheckCircle2, AlertTriangle, Activity, ArrowRight, Filter, ShieldCheck } from "lucide-react";

export const Investigations: React.FC = () => {
  const [statusFilter, setStatusFilter] = useState("ALL");

  const inboxItems = [
    {
      id: "inc-prod-sagemaker-9001",
      title: "Fraud Detection Pipeline",
      status: "Investigating...",
      statusType: "active",
      confidence: 72,
      currentStage: "Building Evidence Graph & Causal Lineage",
      started: "2 minutes ago",
      platform: "WhyLabs Telemetry & OTel Traces",
      severity: "CRITICAL",
    },
    {
      id: "inc-rec-engine-049",
      title: "Recommendation Engine",
      status: "Waiting For Evidence",
      statusType: "pending",
      confidence: 0,
      currentStage: "Awaiting incoming OTel metric buffers",
      started: "12 seconds ago",
      platform: "OpenTelemetry Streaming",
      severity: "WARNING",
    },
    {
      id: "inc-credit-scorer-882",
      title: "Credit Risk Classifier",
      status: "Completed",
      statusType: "completed",
      confidence: 94,
      currentStage: "Recommendation Ready: Rollback Preprocessing V18",
      started: "14 minutes ago",
      platform: "Evidently AI & DriftGuard Governance",
      severity: "CRITICAL",
    },
    {
      id: "inc-llm-summarizer-01",
      title: "LLM Billing Support Agent",
      status: "Completed",
      statusType: "completed",
      confidence: 89,
      currentStage: "Recommendation Ready: Update Prompt Guard Rails",
      started: "45 minutes ago",
      platform: "Arize AI Model Intelligence",
      severity: "WARNING",
    },
  ];

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6 font-sans">
      <div className="flex items-center justify-between border-b border-border pb-5">
        <div>
          <h2 className="text-lg font-bold text-slate-100 tracking-tight">Active Investigations Inbox</h2>
          <p className="text-xs text-slate-400 mt-1">
            Real-time anomaly reasoning loops and engineering change requests triggered after monitoring detection.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="flex items-center bg-slate-900 border border-slate-800 rounded px-3 py-1.5 text-xs text-slate-300 space-x-2">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-transparent text-xs text-slate-200 focus:outline-none cursor-pointer font-medium"
            >
              <option value="ALL">All Investigation Loops</option>
              <option value="active">Active Investigating</option>
              <option value="completed">Recommendation Ready</option>
              <option value="pending">Waiting For Evidence</option>
            </select>
          </div>
        </div>
      </div>

      {/* Investigation Inbox Ledger */}
      <div className="space-y-3.5">
        {inboxItems
          .filter((item) => statusFilter === "ALL" || item.statusType === statusFilter)
          .map((item) => (
            <Link
              key={item.id}
              to={`/investigations/${item.id}`}
              className="block bg-card border border-border rounded-md p-5 hover:border-slate-600 transition-all duration-200 group"
            >
              <div className="flex items-start justify-between">
                <div className="space-y-2">
                  <div className="flex items-center space-x-3">
                    <span className={`w-2.5 h-2.5 rounded-full ${
                      item.statusType === "active" ? "bg-blue-500 animate-pulse" : item.statusType === "completed" ? "bg-emerald-500" : "bg-amber-500"
                    }`} />
                    <span className="text-base font-bold text-slate-100 group-hover:text-blue-400 transition-colors">
                      {item.title}
                    </span>
                    <span className="text-xs font-mono text-slate-500">({item.id})</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase border ${
                      item.severity === "CRITICAL" ? "bg-red-950/80 text-red-300 border-red-800/80" : "bg-amber-950/80 text-amber-300 border-amber-800/80"
                    }`}>
                      {item.severity}
                    </span>
                  </div>

                  <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-xs text-slate-400 font-mono">
                    <div className="flex items-center gap-1.5">
                      <span className="text-slate-500 font-sans">Status:</span>
                      <span className={`font-semibold ${
                        item.statusType === "active" ? "text-blue-400" : item.statusType === "completed" ? "text-emerald-400" : "text-amber-400"
                      }`}>
                        {item.status}
                      </span>
                    </div>
                    {item.confidence > 0 && (
                      <div className="flex items-center gap-1.5">
                        <span className="text-slate-500 font-sans">Confidence:</span>
                        <span className="text-slate-200 font-bold">{item.confidence}%</span>
                      </div>
                    )}
                    <div className="flex items-center gap-1.5">
                      <span className="text-slate-500 font-sans">Stage:</span>
                      <span className="text-slate-300 font-medium">{item.currentStage}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span className="text-slate-500 font-sans">Started:</span>
                      <span className="text-slate-400">{item.started}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center text-xs font-semibold text-blue-400 group-hover:translate-x-1 transition-transform shrink-0 pt-1">
                  <span>Inspect Loop</span>
                  <ArrowRight className="w-3.5 h-3.5 ml-1" />
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-900 flex items-center justify-between text-[11px] font-mono text-slate-400">
                <span>Integrated Evidence Sources: {item.platform}</span>
                <span className="flex items-center gap-1 text-emerald-400">
                  <ShieldCheck className="w-3.5 h-3.5" /> Algorithmic Bayesian Verification Active
                </span>
              </div>
            </Link>
          ))}
      </div>
    </div>
  );
};
