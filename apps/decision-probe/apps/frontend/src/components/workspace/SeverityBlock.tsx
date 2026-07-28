"use client";

import React from 'react';
import { Section } from './BlockRenderer';

export interface SeverityBlockProps {
  block: {
    id: string;
    type: string;
    content: {
      severity?: "SEV1" | "SEV2" | "SEV3" | "SEV4" | string;
      impact_summary?: string;
      reasoning?: string[];
    };
  };
}

export function SeverityBlock({ block }: SeverityBlockProps) {
  const content = block.content || {};
  const severity = content.severity || "SEV3";
  const impact = content.impact_summary || "";
  const reasoning = content.reasoning || [];

  const sevColor = (sev: string) => {
    switch (sev.toUpperCase()) {
      case "SEV1":
        return "bg-red-500/10 text-red-500 border-red-500/30";
      case "SEV2":
        return "bg-amber-500/10 text-amber-500 border-amber-500/30";
      default:
        return "bg-blue-500/10 text-blue-500 border-blue-500/30";
    }
  };

  return (
    <Section title="Incident Severity Assessment">
      <div className="mx-2 rounded-xl border border-border bg-panel/30 p-5 shadow-sm space-y-4 text-[12.5px]">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-border-subtle/50 pb-3">
          <div className="space-y-1">
            <span className="text-micro text-fg-muted font-medium uppercase tracking-wider block mb-0.5">Classification Tag</span>
            <span className={`text-[12px] font-bold uppercase tracking-wider px-2.5 py-1 rounded border ${sevColor(severity)}`}>
              {severity}
            </span>
          </div>
          <div className="flex-1 md:ml-6">
            <strong className="text-foreground font-semibold text-[13px] block mb-1">Impact Summary:</strong>
            <p className="text-fg-muted leading-relaxed">{impact}</p>
          </div>
        </div>

        {reasoning.length > 0 && (
          <div className="space-y-2">
            <strong className="text-fg-muted font-medium text-micro uppercase tracking-wider block">Classification Criteria Reasoning:</strong>
            <ul className="space-y-1.5 list-disc list-inside text-foreground/90">
              {reasoning.map((item, idx) => (
                <li key={idx} className="leading-snug">
                  {item}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </Section>
  );
}
