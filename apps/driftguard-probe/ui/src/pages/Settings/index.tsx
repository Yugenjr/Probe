import React from "react";
import { Shield, Key, Sliders, Lock, Check } from "lucide-react";

export const Settings: React.FC = () => {
  return (
    <div className="p-6 space-y-6 font-sans max-w-4xl mx-auto">
      <div>
        <h2 className="text-base font-semibold text-slate-100">Tenant Workspace Settings & RBAC</h2>
        <p className="text-xs text-slate-400 mt-1">Manage active LLM capability endpoints, sandbox privilege rules, and API token rotations.</p>
      </div>

      <div className="space-y-4">
        {/* Sandbox Privilege Manifests */}
        <div className="bg-card border border-border rounded-md p-5 space-y-3">
          <div className="flex items-center justify-between border-b border-border pb-3">
            <div className="flex items-center space-x-2 font-semibold text-sm text-slate-100">
              <Shield className="w-4 h-4 text-emerald-400" />
              <span>Out-of-Process Plugin Security Mandate</span>
            </div>
            <span className="px-2 py-0.5 bg-emerald-950 text-emerald-300 border border-emerald-800 rounded text-[10px] uppercase font-mono font-semibold">
              Enforced
            </span>
          </div>
          <p className="text-xs text-slate-400">
            All vendor monitoring community plugins execute within secure isolated subprocesses or WebAssembly boundaries. Ambient OS environment keys and database connection pools are blocked from plugin access.
          </p>
          <div className="pt-2 flex justify-end">
            <button className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 rounded text-xs font-medium transition-colors">
              Inspect Whitelisted Domain Manifests
            </button>
          </div>
        </div>

        {/* API Credentials */}
        <div className="bg-card border border-border rounded-md p-5 space-y-3">
          <div className="flex items-center justify-between border-b border-border pb-3">
            <div className="flex items-center space-x-2 font-semibold text-sm text-slate-100">
              <Key className="w-4 h-4 text-blue-400" />
              <span>Tenant API Token Management</span>
            </div>
            <span className="text-xs font-mono text-slate-500">Tenant: Prod-US-East</span>
          </div>
          <div className="space-y-2 font-mono text-xs">
            <label className="text-slate-400">Active Webhook Ingress Key:</label>
            <div className="flex items-center space-x-2">
              <input
                type="password"
                readOnly
                value="probe_live_token_998127391823091820"
                className="w-full bg-slate-900 border border-slate-800 rounded py-1.5 px-3 text-slate-300"
              />
              <button className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white font-sans font-semibold rounded shrink-0 transition-colors">
                Rotate Secret
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
