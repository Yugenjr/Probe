"use client";

import React from 'react';
import { Section } from './BlockRenderer';

export interface ResolutionBlockProps {
  block: {
    id: string;
    type: string;
    content: {
      status?: "resolved" | "monitoring" | "open" | string;
      completed_actions?: string[];
      remaining_risks?: string[];
      summary?: string;
    };
  };
}

export function ResolutionBlock({ block }: ResolutionBlockProps) {
  const content = block.content || {};
  const status = content.status || "open";
  const completed = content.completed_actions || [];
  const risks = content.remaining_risks || [];
  const summary = content.summary || "";

  const statusTag = (s: string) => {
    const base = "text-micro font-bold uppercase tracking-wider px-2 py-0.5 rounded border ";
    if (s === "resolved") {
      return <span className={base + "bg-success/10 text-success border-success/30"}>Resolved</span>;
    }
    if (s === "monitoring") {
      return <span className={base + "bg-warning/10 text-warning border-warning/30"}>Monitoring</span>;
    }
    return <span className={base + "bg-danger/10 text-danger border-danger/30"}>Open</span>;
  };

  return (
    <Section title="Incident Resolution Tracking">
      <div className="mx-2 rounded-xl border border-border bg-panel/30 p-5 shadow-sm space-y-4 text-[12.5px]">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-border-subtle/50 pb-3">
          <div className="space-y-1">
            <span className="text-micro text-fg-muted font-medium uppercase tracking-wider block mb-0.5">Resolution Status</span>
            {statusTag(status)}
          </div>
          {summary && (
            <div className="flex-1 md:ml-6 text-fg-muted leading-relaxed">
              {summary}
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Completed Actions */}
          <div>
            <span className="text-micro text-success font-semibold tracking-wider uppercase block mb-3">
              Completed Actions & Fixes
            </span>
            {completed.length > 0 ? (
              <ul className="space-y-2">
                {completed.map((act, idx) => (
                  <li key={idx} className="flex items-start gap-2 leading-snug">
                    <span className="text-success text-[13px] mt-0.5 font-bold">✓</span>
                    <span className="text-foreground/90">{act}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-fg-muted italic">No completed actions recorded.</p>
            )}
          </div>

          {/* Remaining Risks */}
          <div>
            <span className="text-micro text-warning font-semibold tracking-wider uppercase block mb-3">
              Remaining System Risks
            </span>
            {risks.length > 0 ? (
              <ul className="space-y-2">
                {risks.map((risk, idx) => (
                  <li key={idx} className="flex items-start gap-2 leading-snug">
                    <span className="text-warning text-[14px] mt-0.5">⚠</span>
                    <span className="text-foreground/90">{risk}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-fg-muted italic">No remaining risks identified.</p>
            )}
          </div>
        </div>
      </div>
    </Section>
  );
}
