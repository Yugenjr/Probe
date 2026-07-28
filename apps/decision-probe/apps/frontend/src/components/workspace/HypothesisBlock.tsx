"use client";

import React from 'react';
import { Section } from './BlockRenderer';

export interface Hypothesis {
  id: string;
  title: string;
  description: string;
  supporting_evidence: string[];
  confidence: number;
  assumptions: string[];
}

export interface HypothesisBlockProps {
  block: {
    id: string;
    type: string;
    content: {
      hypotheses: Hypothesis[];
    };
  };
}

export function HypothesisBlock({ block }: HypothesisBlockProps) {
  const hypotheses = block.content?.hypotheses || [];

  return (
    <Section title="Incident Hypotheses" count={hypotheses.length}>
      {hypotheses.length === 0 ? (
        <p className="text-[12.5px] text-fg-muted py-4 italic">No hypotheses generated yet.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
          {hypotheses.map((hyp) => {
            const confPercent = Math.round((hyp.confidence || 0.5) * 100);
            
            // Color based on confidence levels
            let confColor = "text-fg-muted bg-background-soft border-border-subtle";
            if (confPercent >= 70) {
              confColor = "text-success bg-success/5 border-success/10";
            } else if (confPercent >= 40) {
              confColor = "text-warning bg-warning/5 border-warning/10";
            } else {
              confColor = "text-danger bg-danger/5 border-danger/10";
            }

            return (
              <div key={hyp.id} className="border border-border bg-panel/40 hover:bg-panel transition-all duration-200 rounded-xl p-4 flex flex-col justify-between shadow-sm">
                <div>
                  <div className="flex items-center justify-between gap-3 mb-2.5">
                    <span className="mono text-[10px] text-fg-muted font-bold tracking-wide uppercase bg-raised px-1.5 py-0.5 rounded">
                      {hyp.id}
                    </span>
                    <span className={`mono text-[11px] font-semibold border rounded-full px-2 py-0.5 ${confColor}`}>
                      {confPercent}% Conf.
                    </span>
                  </div>

                  <h4 className="text-[13.5px] font-semibold text-fg-strong leading-tight mb-2">
                    {hyp.title}
                  </h4>
                  
                  <p className="text-[12.5px] text-foreground/80 leading-relaxed mb-4">
                    {hyp.description}
                  </p>
                </div>

                <div className="space-y-3 pt-3 border-t border-border-subtle/50 text-[11.5px]">
                  {/* Supporting Evidence */}
                  {hyp.supporting_evidence && hyp.supporting_evidence.length > 0 && (
                    <div>
                      <span className="text-fg-muted font-medium block mb-1">Supporting Evidence:</span>
                      <div className="flex flex-wrap gap-1">
                        {hyp.supporting_evidence.map((ref, idx) => (
                          <span key={idx} className="mono text-[10px] bg-background border border-border-subtle px-1.5 py-0.5 rounded text-accent font-semibold">
                            {ref}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Assumptions */}
                  {hyp.assumptions && hyp.assumptions.length > 0 && (
                    <div>
                      <span className="text-fg-muted font-medium block mb-1">Assumptions:</span>
                      <ul className="list-disc list-inside space-y-0.5 text-fg-muted text-[11px]">
                        {hyp.assumptions.map((asm, idx) => (
                          <li key={idx} className="truncate" title={asm}>{asm}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </Section>
  );
}
