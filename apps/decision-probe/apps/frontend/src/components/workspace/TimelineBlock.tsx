"use client";

import React from 'react';
import { Section } from './BlockRenderer';

export interface TimelineEvent {
  timestamp: string;
  action: string;
}

export interface TimelineBlockProps {
  block: any;
}

export function TimelineBlock({ block }: TimelineBlockProps) {
  const c = block.content || {};
  const events: TimelineEvent[] = c.events || [];

  return (
    <Section title="Timeline" count={events.length}>
      <ol className="relative ml-4">
        <span className="absolute left-[78px] top-3 bottom-3 w-px bg-border-subtle" />
        {events.map((event, i) => {
          let dotColor = 'bg-fg-muted';
          if (event.action.toLowerCase().includes('alert') || event.action.toLowerCase().includes('incident')) dotColor = 'bg-danger';
          else if (event.action.toLowerCase().includes('spike') || event.action.toLowerCase().includes('cpu')) dotColor = 'bg-warning';
          else if (event.action.toLowerCase().includes('deploy') || event.action.toLowerCase().includes('commit')) dotColor = 'bg-info';
          
          return (
            <li key={i} className="fade-in group flex items-start gap-4 py-1.5 text-[12.5px]">
              <span className="mono w-16 shrink-0 pt-0.5 text-[11px] text-fg-muted text-right">{event.timestamp}</span>
              <div className="relative z-10 flex h-4 w-4 shrink-0 items-center justify-center bg-background pt-0.5">
                <span className={`h-2 w-2 rounded-full ${dotColor}`} />
              </div>
              <span className="min-w-0 flex-1 pt-0.5 text-foreground leading-snug">{event.action}</span>
            </li>
          );
        })}
      </ol>
    </Section>
  );
}
