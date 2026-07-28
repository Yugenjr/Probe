"use client";

import React from 'react';
import { Section } from './BlockRenderer';

export interface ChangeItem {
  service: string;
  version: string;
  changed_at: string;
  author: string;
  summary: string;
}

export interface DeploymentChangeBlockProps {
  block: {
    id: string;
    type: string;
    content: {
      changes?: ChangeItem[];
    };
  };
}

export function DeploymentChangeBlock({ block }: DeploymentChangeBlockProps) {
  const content = block.content || {};
  const changes = content.changes || [];

  return (
    <Section title="Deployment Changes" count={changes.length}>
      <div className="mx-2 rounded-xl border border-border bg-panel/30 p-5 shadow-sm">
        {changes.length > 0 ? (
          <div className="space-y-4">
            {changes.map((item, idx) => (
              <div key={idx} className="border border-border-subtle/50 bg-raised/10 rounded-xl p-4 text-[12.5px] space-y-2">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-2.5">
                  <div className="flex items-center gap-2">
                    <span className="bg-accent/15 text-accent border border-accent/25 text-[10.5px] font-bold px-2 py-0.5 rounded">
                      {item.service}
                    </span>
                    <span className="font-semibold text-foreground/90">{item.version}</span>
                  </div>
                  <span className="text-fg-muted text-[11px] font-medium">{item.changed_at}</span>
                </div>
                
                <p className="text-foreground/90 mt-1">
                  <strong className="text-fg-muted font-medium text-micro uppercase tracking-wider block mb-0.5">Deployment Change Summary:</strong>
                  {item.summary}
                </p>
                
                <p className="text-[11px] text-fg-muted">
                  <strong className="text-fg-muted font-medium text-micro uppercase tracking-wider block mb-0.5">Triggered Author:</strong>
                  {item.author}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-[12.5px] text-fg-muted italic">No deployment rollout changes detected.</p>
        )}
      </div>
    </Section>
  );
}
