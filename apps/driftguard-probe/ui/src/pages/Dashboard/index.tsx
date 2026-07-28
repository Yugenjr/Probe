import React from "react";
import { Activity, GitFork, CheckCircle2, AlertTriangle, Layers, Clock, ShieldCheck, ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

export const Dashboard: React.FC = () => {
  const stats = [
    { label: "Active Investigations", value: "3", sub: "+1 over 24h window", icon: Activity, accent: "text-blue-400" },
    { label: "Mean Diagnosis Speed", value: "4.2m", sub: "100% within SLA", icon: Clock, accent: "text-emerald-400" },
    { label: "Connected Monitors", value: "4 Active", sub: "gRPC & Wasm Sandboxes", icon: Layers, accent: "text-slate-300" },
    { label: "Refinement Cycles", value: "98.4%", sub: "Automated verification pass rate", icon: ShieldCheck, accent: "text-emerald-400" },
  ];

  const investigations = [
    { id: "inc-prod-sagemaker-9001", platform: "WhyLabs Observability", trigger: "Wasserstein Covariate Shift", confidence: 0.88, status: "INVESTIGATING", severity: "CRITICAL", duration: "12m elapsed" },
    { id: "inc-checkout-latency-104", platform: "OpenTelemetry Tracing", trigger: "P99 Latency Surge (>450ms)", confidence: 0.94, status: "COMPLETED", severity: "WARNING", duration: "Resolved in 3.4m" },
    { id: "inc-fraud-detector-v2", platform: "Evidently AI Monitor", trigger: "Prediction Drift Alert (PSI 0.31)", confidence: 0.76, status: "REFINING LOOP", severity: "CRITICAL", duration: "18m elapsed" },
  ];

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto font-sans">
      <div>
        <h2 className="text-base font-semibold text-slate-100">Executive Investigation Dashboard</h2>
        <p className="text-xs text-slate-400 mt-1">Real-time anomaly reasoning across third-party telemetry integrations and algorithmic verification loops.</p>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((card, i) => {
          const Icon = card.icon;
          return (
            <div key={i} className="bg-card border border-border rounded-md p-4 flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400 font-medium">{card.label}</span>
                <Icon className={`w-4 h-4 ${card.accent}`} />
              </div>
              <div className="mt-3">
                <div className="text-2xl font-semibold tracking-tight text-slate-100 font-mono">{card.value}</div>
                <div className="text-[11px] text-slate-500 mt-1">{card.sub}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Active Investigations Table */}
      <div className="border border-border bg-card rounded-md overflow-hidden">
        <div className="px-4 py-3 border-b border-border flex items-center justify-between bg-slate-900/40">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-300 font-mono">Live Anomaly Investigations</span>
          <Link to="/investigations" className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1 font-medium">
            View All Records <ArrowRight className="w-3 h-3" />
          </Link>
        </div>
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-border bg-slate-950/60 text-slate-400 font-medium font-mono text-[11px]">
              <th className="py-2.5 px-4">Incident ID</th>
              <th className="py-2.5 px-4">Origin Provider</th>
              <th className="py-2.5 px-4">Anomaly Trigger</th>
              <th className="py-2.5 px-4">Algorithmic Confidence</th>
              <th className="py-2.5 px-4">Severity</th>
              <th className="py-2.5 px-4">Status</th>
              <th className="py-2.5 px-4 text-right">Duration</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border text-slate-300 font-mono">
            {investigations.map((row) => (
              <tr key={row.id} className="hover:bg-slate-900/50 transition-colors">
                <td className="py-3 px-4 font-semibold text-blue-400 hover:underline">
                  <Link to={`/investigations/${row.id}`}>{row.id}</Link>
                </td>
                <td className="py-3 px-4 text-slate-300">{row.platform}</td>
                <td className="py-3 px-4 text-slate-400">{row.trigger}</td>
                <td className="py-3 px-4">
                  <div className="flex items-center space-x-2">
                    <span className={`w-2 h-2 rounded-full ${row.confidence >= 0.8 ? "bg-emerald-500" : "bg-yellow-500"}`}></span>
                    <span className="font-semibold">{row.confidence.toFixed(2)}</span>
                  </div>
                </td>
                <td className="py-3 px-4 font-sans">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-semibold tracking-wide uppercase border ${
                    row.severity === "CRITICAL" ? "bg-red-950 text-red-300 border-red-800/80" : "bg-yellow-950 text-yellow-300 border-yellow-800/80"
                  }`}>
                    {row.severity}
                  </span>
                </td>
                <td className="py-3 px-4 font-sans font-medium text-slate-300">{row.status}</td>
                <td className="py-3 px-4 text-right text-slate-400">{row.duration}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
