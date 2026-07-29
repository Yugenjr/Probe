import React from 'react';
import { Workspace } from '@/store/workspaceStore';
import { Activity, Clock, Server, Shield } from 'lucide-react';
import { Badge } from '../ui/badge';

export function DashboardHeader({ workspace }: { workspace: Workspace }) {
  return (
    <div className="flex flex-col gap-4 mb-8 pt-4">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h1 className="text-[22px] font-bold text-fg-strong tracking-tight">{workspace.title}</h1>
            <Badge variant="danger">CRITICAL</Badge>
          </div>
          <p className="text-[13px] text-fg-muted max-w-2xl">
            Automated root cause analysis and remediation for production incident. 
            Investigating database timeout anomalies in us-east-1.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button className="h-8 px-3 rounded-md bg-raised border border-border-subtle text-[12px] font-medium text-foreground hover:bg-raised/80 transition-colors">
            Export Report
          </button>
          <button className="h-8 px-3 rounded-md bg-accent text-[12px] font-medium text-white hover:bg-accent/90 transition-colors shadow-sm">
            Share Investigation
          </button>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4 mt-2">
        <div className="rounded-lg bg-panel border border-border-subtle p-3 flex items-center gap-3">
          <div className="h-8 w-8 rounded-md bg-info/10 text-info flex items-center justify-center">
            <Activity size={16} />
          </div>
          <div>
            <div className="text-[10px] font-bold tracking-widest text-fg-muted uppercase">Status</div>
            <div className="text-[13px] font-semibold text-fg-strong">Investigating</div>
          </div>
        </div>
        
        <div className="rounded-lg bg-panel border border-border-subtle p-3 flex items-center gap-3">
          <div className="h-8 w-8 rounded-md bg-warning/10 text-warning flex items-center justify-center">
            <Clock size={16} />
          </div>
          <div>
            <div className="text-[10px] font-bold tracking-widest text-fg-muted uppercase">MTTR Impact</div>
            <div className="text-[13px] font-semibold text-fg-strong">+42 mins</div>
          </div>
        </div>

        <div className="rounded-lg bg-panel border border-border-subtle p-3 flex items-center gap-3">
          <div className="h-8 w-8 rounded-md bg-accent/10 text-accent flex items-center justify-center">
            <Server size={16} />
          </div>
          <div>
            <div className="text-[10px] font-bold tracking-widest text-fg-muted uppercase">Affected Systems</div>
            <div className="text-[13px] font-semibold text-fg-strong">prod-db-primary, api-gw</div>
          </div>
        </div>

        <div className="rounded-lg bg-panel border border-border-subtle p-3 flex items-center gap-3">
          <div className="h-8 w-8 rounded-md bg-success/10 text-success flex items-center justify-center">
            <Shield size={16} />
          </div>
          <div>
            <div className="text-[10px] font-bold tracking-widest text-fg-muted uppercase">Lead Agent</div>
            <div className="text-[13px] font-semibold text-fg-strong">DecisionProbe v2</div>
          </div>
        </div>
      </div>
    </div>
  );
}
