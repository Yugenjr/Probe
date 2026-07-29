import React from 'react';
import { Section } from './BlockRenderer';
import { Activity } from 'lucide-react';

export function AnomalyBlock({ block }: { block: any }) {
  const c = block.content || {};
  const anomalies = c.anomalies || [
    { metric: "CPU_IOWAIT", current: "85%", expected: "< 5%", zScore: 9.4 },
    { metric: "DB_CONNECTION_LATENCY", current: "1.2s", expected: "45ms", zScore: 12.1 }
  ];
  
  return (
    <Section title="Detected Anomalies" defaultOpen={true}>
      <div className="px-4">
        <div className="grid gap-3">
          {anomalies.map((anom: any, idx: number) => (
            <div key={idx} className="flex items-center justify-between p-3 rounded-lg border border-danger/30 bg-danger/5">
              <div className="flex items-center gap-3">
                <div className="h-8 w-8 rounded-full bg-danger/10 flex items-center justify-center text-danger">
                  <Activity size={16} />
                </div>
                <div>
                  <div className="text-[12px] font-bold font-mono tracking-tight text-foreground">{anom.metric}</div>
                  <div className="text-[11px] text-fg-muted mt-0.5">
                    Expected: {anom.expected}
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-[14px] font-bold text-danger">{anom.current}</div>
                <div className="text-[10px] font-mono text-danger/80">z-score: {anom.zScore}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Section>
  );
}
