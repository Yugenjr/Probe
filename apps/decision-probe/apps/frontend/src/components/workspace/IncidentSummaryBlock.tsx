"use client";

import React from 'react';
import { Section } from './BlockRenderer';

export interface IncidentSummaryProps {
  block: {
    id: string;
    type: string;
    content: {
      incident_title?: string;
      summary?: string;
      affected_services?: string[];
      root_cause?: string;
      confidence?: number;
      current_status?: "investigating" | "mitigated" | "resolved" | string;
    };
  };
}

export function IncidentSummaryBlock({ block }: IncidentSummaryProps) {
  const content = block.content || {};
  const title = content.incident_title || "Unknown Incident Outage";
  const summary = content.summary || "";
  const services = content.affected_services || [];
  const status = content.current_status || "investigating";
  const confidence = content.confidence !== undefined ? content.confidence : 0.0;

  const statusBadge = (s: string) => {
    const base = "text-micro font-bold uppercase tracking-wider px-2 py-0.5 rounded border ";
    if (s === "resolved") {
      return <span className={base + "bg-success/15 text-success border-success/30"}>Resolved</span>;
    }
    if (s === "mitigated") {
      return <span className={base + "bg-warning/15 text-warning border-warning/30"}>Mitigated</span>;
    }
    return <span className={base + "bg-danger/15 text-danger border-danger/30"}>Investigating</span>;
  };

  return (
    <Section title="Incident Command Overview">
      <div className="mx-2 rounded-xl border border-border bg-panel/30 p-5 shadow-sm space-y-4 text-[12.5px]">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-border-subtle/50 pb-3">
          <div className="space-y-1">
            <h4 className="font-semibold text-foreground text-[14.5px] tracking-tight leading-snug">
              {title}
            </h4>
            <p className="text-fg-muted leading-relaxed max-w-2xl">{summary}</p>
          </div>
          <div className="flex items-center gap-2 self-start md:self-center">
            {statusBadge(status)}
            <span className="bg-raised text-foreground border border-border text-[10px] font-bold px-2 py-0.5 rounded-full">
              {Math.round(confidence * 100)}% Confidence
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <strong className="text-fg-muted font-medium text-micro uppercase tracking-wider block mb-1.5">Affected Services:</strong>
            {services.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {services.map((svc, idx) => (
                  <span key={idx} className="bg-accent/10 text-accent border border-accent/20 font-mono text-[11px] px-2.5 py-0.5 rounded-md">
                    {svc}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-fg-muted italic">No specific service tags flagged.</p>
            )}
          </div>
          {content.root_cause && (
            <div>
              <strong className="text-fg-muted font-medium text-micro uppercase tracking-wider block mb-1.5">Identified Root Cause:</strong>
              <p className="font-semibold text-foreground">{content.root_cause}</p>
            </div>
          )}
        </div>
      </div>
    </Section>
  );
}
