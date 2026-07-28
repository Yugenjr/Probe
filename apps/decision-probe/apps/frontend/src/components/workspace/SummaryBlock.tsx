import React from 'react';
import { Section } from './BlockRenderer';

export interface SummaryBlockProps {
  block: any;
}

export function SummaryBlock({ block }: SummaryBlockProps) {
  const c = block.content || {};

  return (
    <Section title="Summary" defaultOpen={false}>
      {c.points && c.points.length > 0 ? (
        <ol className="space-y-1 px-4">
          {c.points.map((point: string, idx: number) => (
            <li key={idx} className="text-[12.5px] text-foreground flex items-start gap-2">
              <span className="mono text-[11px] text-fg-muted shrink-0 mt-px">{idx + 1}.</span>
              {point}
            </li>
          ))}
        </ol>
      ) : (
        <div className="px-4 text-[12.5px] text-fg-muted">
          {c.text || 'Auto-generated summary will appear once analysis is complete.'}
        </div>
      )}
      {c.timestamp && (
        <div className="px-4 mt-2 mono text-[10.5px] text-fg-muted">
          {new Date(c.timestamp).toLocaleString()}
        </div>
      )}
    </Section>
  );
}
