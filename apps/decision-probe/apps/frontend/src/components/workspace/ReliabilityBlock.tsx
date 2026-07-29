import React from 'react';
import { Section } from './BlockRenderer';
import { ShieldCheck } from 'lucide-react';
import { Progress } from '../ui/progress';

export function ReliabilityBlock({ block }: { block: any }) {
  const c = block.content || {};
  const score = c.reliability_score || 0.9992;
  const target = c.target_slo || 0.9995;
  
  return (
    <Section title="System Reliability (SLO)" defaultOpen={true}>
      <div className="px-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2 text-foreground font-medium text-[13px]">
            <ShieldCheck size={16} className="text-success" />
            Rolling 30-Day Reliability
          </div>
          <div className="text-[14px] font-mono font-bold text-warning">
            {(score * 100).toFixed(3)}%
          </div>
        </div>
        <Progress value={score * 100} indicatorClassName={score >= target ? "bg-success" : "bg-warning"} className="h-2.5" />
        <div className="flex justify-between mt-2 text-[11px] text-fg-muted">
          <span>Target SLO: {(target * 100).toFixed(3)}%</span>
          <span>Error Budget Remaining: 14%</span>
        </div>
      </div>
    </Section>
  );
}
