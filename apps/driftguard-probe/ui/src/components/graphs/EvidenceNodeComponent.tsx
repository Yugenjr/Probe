import React, { memo } from "react";
import { Handle, Position, NodeProps } from "reactflow";
import { Activity, Database, AlertTriangle, ShieldCheck, FileText } from "lucide-react";

export const EvidenceNodeComponent = memo(({ data }: NodeProps) => {
  const getIcon = () => {
    switch (data.evidence_type) {
      case "feature_drift": return <Database className="w-4 h-4 text-blue-400 shrink-0" />;
      case "latency_curve": return <Activity className="w-4 h-4 text-yellow-400 shrink-0" />;
      case "statistical_drift": return <AlertTriangle className="w-4 h-4 text-red-400 shrink-0" />;
      case "runbook_guidance": return <FileText className="w-4 h-4 text-emerald-400 shrink-0" />;
      default: return <ShieldCheck className="w-4 h-4 text-slate-400 shrink-0" />;
    }
  };

  return (
    <div className="min-w-[220px] max-w-[260px] bg-slate-900 border border-slate-700 rounded-md p-3 shadow-sm hover:border-slate-500 transition-colors font-sans select-none">
      <Handle type="target" position={Position.Left} className="w-2.5 h-2.5 bg-slate-500 border-none" />
      <div className="flex items-center space-x-2 border-b border-slate-800 pb-2 mb-2">
        {getIcon()}
        <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-300 font-mono truncate">{data.evidence_type}</span>
        <span className="ml-auto text-[10px] px-1.5 py-0.5 bg-slate-800 text-slate-400 rounded font-mono shrink-0">W: {data.empirical_weight}</span>
      </div>
      <p className="text-[11px] text-slate-200 leading-relaxed font-mono break-words">{data.summary}</p>
      <div className="mt-2.5 pt-2 border-t border-slate-800/80 text-[10px] text-slate-500 flex justify-between font-mono">
        <span>Src: {data.source_provider}</span>
        <span>ID: {data.node_id?.substring(0, 8)}</span>
      </div>
      <Handle type="source" position={Position.Right} className="w-2.5 h-2.5 bg-blue-500 border-none" />
    </div>
  );
});
