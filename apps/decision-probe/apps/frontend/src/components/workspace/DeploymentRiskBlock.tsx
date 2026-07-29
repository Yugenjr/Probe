import React from 'react';
import { Section } from './BlockRenderer';
import { GitCommit } from 'lucide-react';
import { Badge } from '../ui/badge';

export function DeploymentRiskBlock({ block }: { block: any }) {
  const c = block.content || {};
  
  return (
    <Section title="Deployment Risk Analysis" defaultOpen={true}>
      <div className="px-4">
        <div className="p-3 bg-background rounded-lg border border-border-subtle flex items-start gap-3">
          <div className="mt-0.5 text-accent">
            <GitCommit size={18} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[13px] font-semibold text-foreground">Deploy #892 (prod-api)</span>
              <Badge variant="warning">High Risk</Badge>
            </div>
            <p className="text-[12px] text-fg-muted mt-1">
              This deployment changed core database connection pooling logic, correlating strongly with the timing of the current incident.
            </p>
            <div className="mt-3 flex items-center gap-2">
              <button className="text-[11px] bg-raised px-2 py-1 rounded text-foreground hover:bg-raised/80 font-medium">View Diff</button>
              <button className="text-[11px] bg-danger/10 text-danger border border-danger/20 px-2 py-1 rounded font-medium hover:bg-danger/20">Initiate Rollback</button>
            </div>
          </div>
        </div>
      </div>
    </Section>
  );
}
