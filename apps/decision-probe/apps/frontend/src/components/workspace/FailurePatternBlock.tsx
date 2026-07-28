"use client";

import React from 'react';
import { Section } from './BlockRenderer';

export interface FailurePattern {
  pattern: string;
  occurrences: number;
  affected_services: string[];
}

export interface FailurePatternBlockProps {
  block: {
    id: string;
    type: string;
    content: {
      patterns?: FailurePattern[];
    };
  };
}

export function FailurePatternBlock({ block }: FailurePatternBlockProps) {
  const content = block.content || {};
  const patterns = content.patterns || [];

  return (
    <Section title="Detected Failure Patterns" count={patterns.length}>
      <div className="mx-2 rounded-xl border border-border bg-panel/30 p-5 shadow-sm">
        {patterns.length > 0 ? (
          <div className="space-y-4">
            {patterns.map((item, idx) => (
              <div key={idx} className="border border-border-subtle/50 bg-raised/10 rounded-xl p-4 space-y-3.5 text-[12.5px]">
                <div className="flex items-center justify-between border-b border-border-subtle/30 pb-2">
                  <span className="font-semibold text-foreground text-[13px]">{item.pattern}</span>
                  <span className="bg-amber-500/10 text-amber-500 border border-amber-500/25 font-bold px-2 py-0.5 rounded text-[11px]">
                    {item.occurrences} Occurrences
                  </span>
                </div>
                
                <div>
                  <strong className="text-fg-muted font-medium text-micro uppercase tracking-wider block mb-1.5">Affected Services:</strong>
                  <div className="flex flex-wrap gap-2">
                    {item.affected_services.map((svc, sIdx) => (
                      <span key={sIdx} className="bg-accent/10 text-accent border border-accent/20 font-mono text-[11px] px-2.5 py-0.5 rounded-md">
                        {svc}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-[12.5px] text-fg-muted italic">No recurring pattern aggregates identified.</p>
        )}
      </div>
    </Section>
  );
}
