import React from "react";
import { Layers, CheckCircle2, Shield, Settings2, Terminal, RefreshCw } from "lucide-react";

export const ConnectedPlatforms: React.FC = () => {
  const platforms = [
    {
      id: "driftguard",
      name: "DriftGuard Enterprise Governance",
      status: "Connected (gRPC)",
      version: "SDK v2.4.0",
      sync: "12 seconds ago",
      models: 18,
      sandbox: "Out-of-Process Binary",
      statusColor: "text-emerald-400",
    },
    {
      id: "whylabs",
      name: "WhyLabs Telemetry Observability",
      status: "Connected (Wasm IPC)",
      version: "Profile-v0.2",
      sync: "1 minute ago",
      models: 6,
      sandbox: "Wasm Sandbox",
      statusColor: "text-emerald-400",
    },
    {
      id: "evidently",
      name: "Evidently AI Statistical Monitor",
      status: "Connected (Subprocess)",
      version: "v0.4.11",
      sync: "4 minutes ago",
      models: 4,
      sandbox: "Subprocess Permit",
      statusColor: "text-emerald-400",
    },
    {
      id: "arize",
      name: "Arize AI Model Intelligence",
      status: "Disconnected (Offline)",
      version: "SDK v3.1.0",
      sync: "2 hours ago",
      models: 0,
      sandbox: "Subprocess Permit",
      statusColor: "text-slate-500",
    },
  ];

  return (
    <div className="p-6 space-y-6 font-sans max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-slate-100">Connected Monitoring Providers & Sandbox Studio</h2>
          <p className="text-xs text-slate-400 mt-1">Manage zero-trust out-of-process IPC capabilities and secure third-party vendor integrations.</p>
        </div>
        <button className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold rounded text-xs transition-colors flex items-center gap-2 border border-slate-700">
          <RefreshCw className="w-3.5 h-3.5" /> Force Webhook Re-sync
        </button>
      </div>

      {/* Integration Providers Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {platforms.map((p) => (
          <div key={p.id} className="bg-card border border-border rounded-md p-5 space-y-4 flex flex-col justify-between">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2.5">
                  <Layers className="w-5 h-5 text-blue-400" />
                  <span className="font-semibold text-sm text-slate-100">{p.name}</span>
                </div>
              </div>
              <div className="flex items-center space-x-2 font-mono text-xs">
                <CheckCircle2 className={`w-4 h-4 ${p.statusColor}`} />
                <span className={p.status === "Disconnected (Offline)" ? "text-slate-500" : "text-slate-300 font-medium"}>
                  {p.status}
                </span>
                <span className="text-slate-700">|</span>
                <span className="text-slate-400">Sync: {p.sync}</span>
              </div>
            </div>

            <div className="bg-slate-950 border border-slate-900 rounded p-3 text-xs font-mono space-y-1.5 text-slate-400">
              <div className="flex justify-between">
                <span>Adapter Version:</span>
                <span className="text-slate-300">{p.version}</span>
              </div>
              <div className="flex justify-between">
                <span>Active Monitored Models:</span>
                <span className="text-slate-200 font-semibold">{p.models} Active Streams</span>
              </div>
              <div className="flex justify-between">
                <span>Sandbox Architecture:</span>
                <span className="text-emerald-400 flex items-center gap-1">
                  <Shield className="w-3 h-3" /> {p.sandbox}
                </span>
              </div>
            </div>

            <div className="flex justify-end pt-2 border-t border-border/60">
              <button className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 rounded text-xs font-medium transition-colors flex items-center gap-2 font-sans">
                <Settings2 className="w-3.5 h-3.5 text-slate-400" /> Configure Sandbox Permissions
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
