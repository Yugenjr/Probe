"use client";

import React, { useState, type ReactNode } from 'react';
import { ChartBlock } from './ChartBlock';
import { EvidenceBlock } from './EvidenceBlock';
import { DecisionBlock } from './DecisionBlock';
import { TimelineBlock } from './TimelineBlock';
import { IncidentBlock } from './IncidentBlock';
import { ReasoningBlock } from './ReasoningBlock';
import { SummaryBlock } from './SummaryBlock';
import { Block } from '@/store/workspaceStore';

const BlockRegistry: Record<string, React.FC<{ block: Block }>> = {
  incident: IncidentBlock,
  evidence: EvidenceBlock,
  timeline: TimelineBlock,
  decision: DecisionBlock,
  summary: SummaryBlock,
  chart: ChartBlock,
  reasoning: ReasoningBlock
};

export function BlockRenderer({ block }: { block: Block }) {
  const Component = BlockRegistry[block.type];
  if (Component) return <Component block={block} />;
  return (
    <Section title={block.type} defaultOpen>
      <pre className="px-4 text-[12.5px] mono text-fg-muted whitespace-pre-wrap overflow-x-auto">
        {JSON.stringify(block.content, null, 2)}
      </pre>
    </Section>
  );
}

/** Shared collapsible section — matches lovable-frontend's Section component exactly */
export function Section({
  title, count, defaultOpen = true, action, children,
}: {
  title: string; count?: number | string; defaultOpen?: boolean; action?: ReactNode; children: ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <section className="mb-8">
      <header className="sticky top-0 z-10 flex h-8 items-center bg-background">
        <button
          onClick={() => setOpen(v => !v)}
          className="group flex flex-1 items-center gap-2 pr-2 text-left"
        >
          <span className="mono w-3 text-[11px] text-fg-muted transition-transform" style={{ transform: open ? 'rotate(90deg)' : 'none' }}>›</span>
          <span className="text-micro">{title}</span>
          {count !== undefined && <span className="mono text-[10.5px] text-fg-muted">· {count}</span>}
        </button>
        {action && open && <div className="pr-4">{action}</div>}
      </header>
      {open && <div className="fade-in pt-1 pb-4">{children}</div>}
    </section>
  );
}

/** Row helper — matches lovable-frontend's Row component */
export function Row({ children, onClick }: { children: ReactNode; onClick?: () => void }) {
  return (
    <div
      onClick={onClick}
      className="group flex h-7 cursor-default items-center gap-3 px-4 text-[12.5px] transition-colors hover:bg-raised/50"
    >
      {children}
    </div>
  );
}
