"use client";

import React from 'react';
import { Section } from './BlockRenderer';

export interface RemediationBlockProps {
  block: {
    id: string;
    type: string;
    content: {
      immediate_actions?: string[];
      permanent_fixes?: string[];
      prevention_steps?: string[];
      summary?: string;
    };
  };
}

export function RemediationBlock({ block }: RemediationBlockProps) {
  const content = block.content || {};
  const immediate = content.immediate_actions || [];
  const permanent = content.permanent_fixes || [];
  const prevention = content.prevention_steps || [];
  const summary = content.summary || "";

  return (
    <Section title="Remediation Plan">
      <div className="mx-2 rounded-xl border border-border bg-panel/30 p-5 shadow-sm">
        {summary && (
          <div className="mb-5 text-[12.5px] leading-relaxed bg-raised/20 border border-border-subtle/50 rounded-xl p-4 text-foreground/90">
            <span className="text-micro text-fg-muted uppercase tracking-wider block mb-1.5">Remediation Strategy Overview</span>
            <p>{summary}</p>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-[12.5px]">
          {/* Immediate Actions */}
          <div className="bg-raised/10 border border-border-subtle/40 rounded-xl p-4">
            <span className="text-micro text-danger font-semibold tracking-wider uppercase block mb-3">
              Immediate Actions
            </span>
            {immediate.length > 0 ? (
              <ul className="space-y-2.5">
                {immediate.map((act, i) => (
                  <li key={i} className="flex items-start gap-2 leading-snug">
                    <span className="text-danger mt-0.5 select-none font-bold">›</span>
                    <span className="text-foreground/90">{act}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-fg-muted italic">No immediate recovery actions recommended.</p>
            )}
          </div>

          {/* Permanent Fixes */}
          <div className="bg-raised/10 border border-border-subtle/40 rounded-xl p-4">
            <span className="text-micro text-success font-semibold tracking-wider uppercase block mb-3">
              Permanent Fixes
            </span>
            {permanent.length > 0 ? (
              <ul className="space-y-2.5">
                {permanent.map((fix, i) => (
                  <li key={i} className="flex items-start gap-2 leading-snug">
                    <span className="text-success mt-0.5 select-none font-bold">›</span>
                    <span className="text-foreground/90">{fix}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-fg-muted italic">No permanent fixes recommended.</p>
            )}
          </div>

          {/* Prevention Steps */}
          <div className="bg-raised/10 border border-border-subtle/40 rounded-xl p-4">
            <span className="text-micro text-accent font-semibold tracking-wider uppercase block mb-3">
              Prevention Steps
            </span>
            {prevention.length > 0 ? (
              <ul className="space-y-2.5">
                {prevention.map((prev, i) => (
                  <li key={i} className="flex items-start gap-2 leading-snug">
                    <span className="text-accent mt-0.5 select-none font-bold">›</span>
                    <span className="text-foreground/90">{prev}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-fg-muted italic">No prevention safeguards recommended.</p>
            )}
          </div>
        </div>
      </div>
    </Section>
  );
}
