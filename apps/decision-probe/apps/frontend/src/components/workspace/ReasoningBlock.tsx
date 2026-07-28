import React from 'react';
import { Section } from './BlockRenderer';

export interface ReasoningBlockProps {
  block: any;
}

export function ReasoningBlock({ block }: ReasoningBlockProps) {
  const c = block.content || {};

  return (
    <Section title="Reasoning">
      <div className="ml-4 pl-4 border-l border-border-subtle py-1 space-y-4 text-[12.5px]">
        {c.observation && (
          <div>
            <div className="text-micro mb-0.5 text-fg-muted">Observation</div>
            <div className="text-foreground leading-relaxed">{c.observation}</div>
          </div>
        )}
        {c.inference && (
          <div>
            <div className="text-micro mb-0.5 text-fg-muted">Inference</div>
            <div className="text-foreground leading-relaxed">{c.inference}</div>
          </div>
        )}
        {(c.analysis || c.text) && !c.observation && (
          <div>
            <div className="text-micro mb-0.5 text-fg-muted">Analysis</div>
            <div className="text-foreground leading-relaxed">{c.analysis || c.text}</div>
          </div>
        )}
        {c.evidence_used && (
          <div>
            <div className="text-micro mb-0.5 text-fg-muted">Evidence</div>
            <div className="mono text-[11px] text-fg-muted">
              {(Array.isArray(c.evidence_used) ? c.evidence_used : [c.evidence_used]).join(' · ')}
            </div>
          </div>
        )}
      </div>
    </Section>
  );
}
