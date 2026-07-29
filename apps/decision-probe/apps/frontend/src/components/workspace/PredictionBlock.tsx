import React from 'react';
import { Section } from './BlockRenderer';
import { Progress } from '../ui/progress';
import { BrainCircuit } from 'lucide-react';

export function PredictionBlock({ block }: { block: any }) {
  const c = block.content || {};
  const predictions = c.predictions || [
    { label: "Database Connection Pool Exhaustion", probability: 0.92, time: "T+15m" },
    { label: "API Gateway 503 Cascading", probability: 0.78, time: "T+45m" },
    { label: "Cache Layer Eviction Storm", probability: 0.45, time: "T+90m" }
  ];
  
  return (
    <Section title="AI Failure Predictions" defaultOpen={true}>
      <div className="px-4 space-y-4">
        <div className="flex items-center gap-2 text-[12px] text-fg-muted mb-2">
          <BrainCircuit size={14} className="text-accent" />
          <span>Machine learning models predict the following impending events based on current trajectory:</span>
        </div>
        
        {predictions.map((pred: any, idx: number) => (
          <div key={idx} className="bg-background rounded-lg border border-border-subtle p-3">
            <div className="flex justify-between items-center mb-2 text-[12.5px]">
              <span className="font-medium text-foreground">{pred.label}</span>
              <div className="flex items-center gap-3">
                <span className="font-mono text-[11px] text-fg-muted bg-raised px-1.5 py-0.5 rounded">{pred.time}</span>
                <span className="font-mono font-bold">{Math.round(pred.probability * 100)}%</span>
              </div>
            </div>
            <Progress 
              value={pred.probability * 100} 
              indicatorClassName={pred.probability > 0.8 ? "bg-danger" : pred.probability > 0.6 ? "bg-warning" : "bg-accent"} 
            />
          </div>
        ))}
      </div>
    </Section>
  );
}
