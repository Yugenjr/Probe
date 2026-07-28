import React from "react";
import { FileText, Download, Check, Calendar, Shield } from "lucide-react";

export const Reports: React.FC = () => {
  const reports = [
    { id: "REP-20260726-01", title: "Regulatory Root-Cause Audit: inc-prod-sagemaker-9001", date: "July 26, 2026", format: "PDF / JSON", status: "Verified", author: "Causal Synthesis & Architect Roster" },
    { id: "REP-20260725-09", title: "SLA Post-Mortem: Payment Routing Latency Degradation", date: "July 25, 2026", format: "PDF / JSON", status: "Verified", author: "Intervention Architect" },
    { id: "REP-20260724-14", title: "Weekly Demographic Covariate Drift Compliance Log", date: "July 24, 2026", format: "PDF / JSON", status: "Archival", author: "System Automated" },
  ];

  return (
    <div className="p-6 space-y-6 font-sans max-w-7xl mx-auto">
      <div>
        <h2 className="text-base font-semibold text-slate-100">Regulatory & Compliance Audit Reports</h2>
        <p className="text-xs text-slate-400 mt-1">Export tamper-proof serializable investigation journals and explainable post-mortems for regulatory verification.</p>
      </div>

      <div className="border border-border bg-card rounded-md divide-y divide-border">
        {reports.map((rep) => (
          <div key={rep.id} className="p-4 flex items-center justify-between hover:bg-slate-900/40 transition-colors">
            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <FileText className="w-4 h-4 text-blue-400" />
                <span className="font-semibold text-xs text-slate-200 font-mono">{rep.id}:</span>
                <span className="font-semibold text-sm text-slate-100">{rep.title}</span>
              </div>
              <div className="flex items-center space-x-3 text-xs text-slate-400 pl-6 font-mono">
                <span className="flex items-center gap-1"><Calendar className="w-3 h-3 text-slate-500" /> {rep.date}</span>
                <span>|</span>
                <span>Author: {rep.author}</span>
                <span>|</span>
                <span className="text-emerald-400 flex items-center gap-1"><Shield className="w-3 h-3" /> {rep.status}</span>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <button className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 rounded text-xs font-mono font-semibold transition-colors flex items-center gap-1.5">
                <Download className="w-3.5 h-3.5 text-slate-400" /> Export PDF
              </button>
              <button className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 rounded text-xs font-mono font-semibold transition-colors flex items-center gap-1.5">
                <Download className="w-3.5 h-3.5 text-slate-400" /> Export JSON
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
