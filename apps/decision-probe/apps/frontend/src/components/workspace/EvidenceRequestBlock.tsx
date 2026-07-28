"use client";

import React from 'react';
import { Section } from './BlockRenderer';

export interface EvidenceRequestItem {
  type: "log" | "metric" | "config" | "trace";
  source: string;
  query: string;
  time_range: string;
}

export interface EvidenceRequestBlockProps {
  block: {
    id: string;
    type: string;
    content: {
      requests?: EvidenceRequestItem[];
    };
  };
}

export function EvidenceRequestBlock({ block }: EvidenceRequestBlockProps) {
  const content = block.content || {};
  const requests = content.requests || [];

  const typeBadge = (type: string) => {
    const base = "text-micro font-semibold uppercase tracking-wider px-2 py-0.5 rounded border ";
    switch (type) {
      case "metric":
        return <span className={base + "bg-blue-500/10 text-blue-400 border-blue-500/25"}>Metric</span>;
      case "log":
        return <span className={base + "bg-purple-500/10 text-purple-400 border-purple-500/25"}>Log</span>;
      case "config":
        return <span className={base + "bg-amber-500/10 text-amber-400 border-amber-500/25"}>Config</span>;
      default:
        return <span className={base + "bg-teal-500/10 text-teal-400 border-teal-500/25"}>Trace</span>;
    }
  };

  return (
    <Section title="Requested Evidence" count={requests.length}>
      <div className="mx-2 rounded-xl border border-border bg-panel/30 p-5 shadow-sm">
        {requests.length > 0 ? (
          <div className="space-y-4">
            {requests.map((req, idx) => (
              <div key={idx} className="flex flex-col md:flex-row md:items-center justify-between gap-4 border border-border-subtle/50 bg-raised/10 rounded-xl p-4 text-[12.5px]">
                <div className="space-y-2 flex-1">
                  <div className="flex items-center gap-2.5">
                    <span className="font-semibold text-foreground/90 text-sm">#{idx + 1}</span>
                    {typeBadge(req.type)}
                    <span className="text-fg-muted font-medium">| Source: {req.source}</span>
                  </div>
                  <div className="space-y-1">
                    <p className="text-foreground/95">
                      <strong className="text-fg-muted font-medium text-micro uppercase tracking-wider block mb-0.5">Telemetry Query:</strong>
                      <code>{req.query}</code>
                    </p>
                    <p className="text-fg-muted text-[11.5px] mt-1.5">
                      <strong className="text-fg-muted font-medium text-micro uppercase tracking-wider block mb-0.5">Target Time Window:</strong>
                      {req.time_range}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 self-start md:self-center border border-warning/25 bg-warning/5 text-warning text-micro uppercase tracking-wider font-bold rounded-lg px-3 py-1.5 shadow-sm">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-warning opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-warning"></span>
                  </span>
                  Waiting
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-[12.5px] text-fg-muted italic">No evidence collection requests generated.</p>
        )}
      </div>
    </Section>
  );
}
