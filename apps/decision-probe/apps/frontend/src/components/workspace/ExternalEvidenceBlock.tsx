"use client";

import React from 'react';
import { Section } from './BlockRenderer';

export interface LogItem {
  timestamp: string;
  service: string;
  level: "ERROR" | "WARN" | "INFO" | string;
  message: string;
}

export interface ExternalEvidenceBlockProps {
  block: {
    id: string;
    type: string;
    content: {
      logs?: LogItem[];
    };
  };
}

export function ExternalEvidenceBlock({ block }: ExternalEvidenceBlockProps) {
  const content = block.content || {};
  const logs = content.logs || [];

  const levelColor = (level: string) => {
    switch (level.toUpperCase()) {
      case "ERROR":
        return "bg-danger text-danger-foreground border-danger/40";
      case "WARN":
        return "bg-warning text-warning-foreground border-warning/40";
      default:
        return "bg-success text-success-foreground border-success/40";
    }
  };

  return (
    <Section title="External Evidence: Logs" count={logs.length}>
      <div className="mx-2 rounded-xl border border-border bg-panel/30 p-5 shadow-sm">
        {logs.length > 0 ? (
          <div className="space-y-3 font-mono text-[11.5px] leading-relaxed">
            {logs.map((log, idx) => (
              <div key={idx} className="flex flex-col md:flex-row md:items-start gap-2.5 border border-border-subtle/50 bg-raised/10 rounded-xl p-3.5">
                <div className="flex items-center gap-2">
                  <span className="text-fg-muted whitespace-nowrap">{log.timestamp}</span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${levelColor(log.level)}`}>
                    {log.level}
                  </span>
                </div>
                <div className="flex-1">
                  <span className="text-accent font-semibold block md:inline md:mr-2">[{log.service}]</span>
                  <span className="text-foreground/90">{log.message}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-[12.5px] text-fg-muted italic">No external application logs collected.</p>
        )}
      </div>
    </Section>
  );
}
