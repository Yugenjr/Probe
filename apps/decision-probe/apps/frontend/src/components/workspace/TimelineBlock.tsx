"use client";

import React from 'react';
import { Section } from './BlockRenderer';

export interface TimelineEvent {
  timestamp: string;
  type: string;
  service: string;
  description: string;
  source_chunk: string;
}

export interface TimelineBlockProps {
  block: {
    id: string;
    type: string;
    content: {
      events: TimelineEvent[];
    };
  };
}

export function TimelineBlock({ block }: TimelineBlockProps) {
  const events = block.content?.events || [];

  const formatTime = (isoString: string) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
    } catch {
      return isoString;
    }
  };

  const formatDate = (isoString: string) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    } catch {
      return '';
    }
  };

  return (
    <Section title="Investigation Timeline" count={events.length}>
      {events.length === 0 ? (
        <p className="text-[12.5px] text-fg-muted py-4 italic">No timeline events extracted yet.</p>
      ) : (
        <div className="relative ml-2 pl-4 border-l border-border-subtle py-2">
          {events.map((event, idx) => {
            // Determine styling based on event type
            let dotColor = 'bg-fg-muted border-background';
            let tagColor = 'bg-background-soft border-border-subtle text-fg-muted';
            
            const eventType = (event.type || 'info').toLowerCase();
            if (eventType === 'error') {
              dotColor = 'bg-danger border-background ring-4 ring-danger/10';
              tagColor = 'bg-danger/5 border-danger/10 text-danger';
            } else if (eventType === 'warning') {
              dotColor = 'bg-warning border-background ring-4 ring-warning/10';
              tagColor = 'bg-warning/5 border-warning/10 text-warning';
            } else if (eventType === 'deployment') {
              dotColor = 'bg-info border-background ring-4 ring-info/10';
              tagColor = 'bg-info/5 border-info/10 text-info';
            } else if (eventType === 'alert') {
              dotColor = 'bg-danger border-background ring-4 ring-danger/10';
              tagColor = 'bg-danger/5 border-danger/10 text-danger';
            }

            return (
              <div key={idx} className="relative mb-6 last:mb-2 group">
                {/* Timeline Dot */}
                <div className="absolute -left-[21.5px] top-1.5 flex h-3 w-3 items-center justify-center rounded-full bg-background">
                  <span className={`h-2 w-2 rounded-full border ${dotColor}`} />
                </div>

                {/* Event Details */}
                <div className="flex flex-col gap-1 pl-2">
                  <div className="flex flex-wrap items-center gap-2 text-[11px] text-fg-muted">
                    <span className="mono font-semibold bg-background-soft px-1.5 py-0.5 rounded text-foreground">
                      {formatTime(event.timestamp)}
                    </span>
                    <span>{formatDate(event.timestamp)}</span>

                    {event.service && event.service !== 'unknown' && (
                      <span className="mono uppercase bg-background border border-border-subtle px-1 rounded text-[9.5px]">
                        {event.service}
                      </span>
                    )}

                    <span className={`mono rounded px-1.5 text-[9px] border ${tagColor}`}>
                      {eventType}
                    </span>
                  </div>

                  <p className="text-[13px] text-foreground leading-snug mt-1 max-w-3xl">
                    {event.description}
                  </p>

                  {event.source_chunk && (
                    <div className="mt-1 flex items-center gap-1.5">
                      <span className="text-[10px] text-fg-muted font-medium">Source:</span>
                      <span className="mono text-[10px] text-accent font-semibold bg-accent/5 px-1 py-0.5 rounded border border-accent/10">
                        {event.source_chunk}
                      </span>
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
