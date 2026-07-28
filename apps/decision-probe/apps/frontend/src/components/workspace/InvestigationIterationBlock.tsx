"use client";

import React from 'react';
import { Section } from './BlockRenderer';

export interface IterationItem {
  iteration: number;
  status: "completed" | "waiting_for_evidence" | "insufficient";
  confidence_change: {
    before: number;
    after: number;
  };
  reason: string;
}

export interface InvestigationIterationBlockProps {
  block: {
    id: string;
    type: string;
    content: {
      iterations?: IterationItem[];
    };
  };
}

export function InvestigationIterationBlock({ block }: InvestigationIterationBlockProps) {
  const content = block.content || {};
  const iterations = content.iterations || [];

  const statusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "text-success border-success/35 bg-success/5";
      case "waiting_for_evidence":
        return "text-warning border-warning/35 bg-warning/5";
      default:
        return "text-danger border-danger/35 bg-danger/5";
    }
  };

  return (
    <Section title="Investigation Iterations" count={iterations.length}>
      <div className="mx-2 rounded-xl border border-border bg-panel/30 p-5 shadow-sm">
        {iterations.length > 0 ? (
          <div className="relative border-l-2 border-border-subtle/80 pl-6 ml-2.5 space-y-6">
            {iterations.map((item, idx) => (
              <div key={idx} className="relative">
                {/* Timeline node circle */}
                <span className="absolute -left-[32px] top-0 flex h-4 w-4 items-center justify-center rounded-full bg-raised border-2 border-border ring-4 ring-background/25"></span>
                
                <div className="border border-border-subtle/50 bg-raised/10 rounded-xl p-4 text-[12.5px] space-y-3 shadow-xs">
                  <div className="flex items-center justify-between gap-3">
                    <span className="font-semibold text-sm text-foreground">
                      Iteration {item.iteration}
                    </span>
                    <span className={`text-[10.5px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${statusColor(item.status)}`}>
                      {item.status.replace(/_/g, " ")}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-4 bg-raised/20 border border-border-subtle/25 rounded-xl p-3 text-center">
                    <div>
                      <span className="text-[10px] text-fg-muted font-medium uppercase tracking-wider block mb-0.5">Confidence Before</span>
                      <span className="text-sm font-semibold text-foreground/80">{Math.round(item.confidence_change.before * 100)}%</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-fg-muted font-medium uppercase tracking-wider block mb-0.5">Confidence After</span>
                      <span className="text-sm font-semibold text-foreground">{Math.round(item.confidence_change.after * 100)}%</span>
                    </div>
                  </div>

                  <p className="text-fg-muted leading-relaxed">
                    <strong className="text-foreground/90 font-medium text-micro uppercase tracking-wider block mb-0.5">Diagnostic Outcome:</strong>
                    {item.reason}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-[12.5px] text-fg-muted italic">No investigation iteration cycles recorded.</p>
        )}
      </div>
    </Section>
  );
}
