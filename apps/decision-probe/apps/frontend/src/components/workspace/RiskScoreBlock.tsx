import React from 'react';
import { Section } from './BlockRenderer';
import { ConfidenceRing } from '../ui/confidence-ring';
import { Badge } from '../ui/badge';
import { AlertTriangle, TrendingUp } from 'lucide-react';

export function RiskScoreBlock({ block }: { block: any }) {
  const c = block.content || {};
  const score = c.score || 0.85;
  const trend = c.trend || 'increasing';
  
  return (
    <Section title="System Risk Score" defaultOpen={true}>
      <div className="flex items-center gap-6 px-4">
        <ConfidenceRing score={score} size={80} strokeWidth={8} />
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h4 className="text-[14px] font-semibold">High Outage Probability</h4>
            <Badge variant="danger">Critical Risk</Badge>
          </div>
          <p className="text-[12px] text-fg-muted">
            The current system telemetry indicates a high probability of compounding failures within the next 2 hours.
          </p>
          <div className="mt-3 flex items-center gap-4 text-[11px] font-medium">
            <div className="flex items-center gap-1.5 text-danger">
              <TrendingUp size={14} />
              <span>Risk {trend} rapidly</span>
            </div>
            <div className="flex items-center gap-1.5 text-warning">
              <AlertTriangle size={14} />
              <span>3 dependent services at risk</span>
            </div>
          </div>
        </div>
      </div>
    </Section>
  );
}
