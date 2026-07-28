"use client";

import React from 'react';
import { Section } from './BlockRenderer';

export interface EvidenceGapItem {
  gap: string;
  importance: "high" | "medium" | "low";
  required_source: str;
  reason: string;
}

export interface EvidenceGapBlockProps {
  block: {
    id: string;
    type: string;
    content: {
      evidence_gaps?: EvidenceGapItem[];
      should_continue?: boolean;
    };
  };
}

export function EvidenceGapBlock({ block }: EvidenceGapBlockProps) {
  const content = block.content || {};
  const gaps = content.evidence_gaps || [];

  const importanceBadge = (importance: string) => {
    switch (importance) {
      case "high":
        return <span className="bg-danger/10 text-danger border border-danger/20 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase">High Priority</span>;
      case "medium":
        return <span className="bg-warning/10 text-warning border border-warning/20 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase">Medium Priority</span>;
      default:
        return <span className="bg-accent/10 text-accent border border-accent/20 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase">Low Priority</span>;
    }
  };

  return (
    <Section title="Evidence Gaps" count={gaps.length}>
      <div className="mx-2 rounded-xl border border-border bg-panel/30 p-5 shadow-sm">
        {gaps.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {gaps.map((item, idx) => (
              <div key={idx} className="flex flex-col justify-between border border-border-subtle/50 bg-raised/10 rounded-xl p-4 text-[12px] space-y-2.5">
                <div className="flex items-center justify-between gap-3">
                  <span className="font-semibold text-foreground text-[12.5px] leading-snug">
                    {item.gap}
                  </span>
                  {importanceBadge(item.importance)}
                </div>
                
                <div className="space-y-1">
                  <p className="text-fg-muted">
                    <strong className="text-foreground/90 font-medium text-micro uppercase tracking-wider block mb-0.5">Required Source:</strong>
                    {item.required_source}
                  </p>
                  <p className="text-fg-muted mt-1 leading-normal">
                    <strong className="text-foreground/90 font-medium text-micro uppercase tracking-wider block mb-0.5">Investigation Reason:</strong>
                    {item.reason}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-[12.5px] text-fg-muted italic">No evidence gaps identified. The analysis has sufficient supporting diagnostics.</p>
        )}
      </div>
    </Section>
  );
}
