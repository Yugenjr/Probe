import React from 'react';
import { Section } from './BlockRenderer';

export interface EvidenceBlockProps {
  block: any;
}

export function EvidenceBlock({ block }: EvidenceBlockProps) {
  const c = block.content || {};
  
  const type = (c.type || c.source || 'file').toUpperCase();
  const relevance = c.relevance || 0.88;
  const time = c.timestamp || new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'});

  return (
    <Section title="Evidence" count={1}>
      <div className="group flex h-8 items-center gap-4 text-[12.5px] transition-colors hover:bg-raised/40 rounded pr-4 pl-4">
        <span className="mono w-3 text-[10px] text-fg-muted">›</span>
        <span className="w-24 shrink-0 text-micro text-fg-muted truncate">{type}</span>
        <span className="min-w-0 flex-1 truncate text-foreground">{c.title || 'Untitled'}</span>
        <span className="mono text-[11px] text-fg-muted w-12 text-right">{time}</span>
        <span className="mono text-[11px] text-accent w-10 text-right">{relevance.toFixed(2)}</span>
      </div>
    </Section>
  );
}
