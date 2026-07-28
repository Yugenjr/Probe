"use client";

import React from 'react';
import { Section } from './BlockRenderer';

export interface ValidationStep {
  action: string;
  reason: string;
}

export interface ValidationBlockProps {
  block: {
    id: string;
    type: string;
    content: {
      validation_plan?: ValidationStep[];
      missing_information?: string[];
      validation_summary?: string;
    };
  };
}

export function ValidationBlock({ block }: ValidationBlockProps) {
  const content = block.content || {};
  const plan = content.validation_plan || [];
  const missing = content.missing_information || [];
  const summary = content.validation_summary || "";

  return (
    <Section title="Root Cause Validation" count={plan.length}>
      <div className="mx-2 rounded-xl border border-border bg-panel/30 p-5 shadow-sm">
        {summary && (
          <div className="mb-5 text-[12.5px] leading-relaxed bg-raised/20 border border-border-subtle/50 rounded-xl p-4 text-foreground/90">
            <span className="text-micro text-fg-muted uppercase tracking-wider block mb-1.5">Validation Assessment Summary</span>
            <p>{summary}</p>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-[12.5px]">
          {/* Validation Steps */}
          <div>
            <span className="text-micro text-success font-semibold tracking-wider uppercase block mb-3">
              Validation Verification Steps
            </span>
            {plan.length > 0 ? (
              <ul className="space-y-3.5">
                {plan.map((step, idx) => (
                  <li key={idx} className="flex items-start gap-2.5 leading-snug">
                    <span className="text-success text-[13px] select-none mt-0.5 font-bold">✓</span>
                    <div>
                      <p className="font-semibold text-foreground">{step.action}</p>
                      {step.reason && (
                        <p className="text-[11px] text-fg-muted mt-0.5">{step.reason}</p>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-fg-muted italic">No validation steps suggested.</p>
            )}
          </div>

          {/* Missing Information */}
          <div>
            <span className="text-micro text-warning font-semibold tracking-wider uppercase block mb-3">
              Missing Evidence Gaps
            </span>
            {missing.length > 0 ? (
              <ul className="space-y-3">
                {missing.map((info, idx) => (
                  <li key={idx} className="flex items-start gap-2.5 leading-snug">
                    <span className="text-warning text-[14px] select-none mt-0.5">⚠</span>
                    <div>
                      <p className="font-medium text-foreground">{info}</p>
                      <p className="text-[10.5px] text-fg-muted mt-0.5">Required to fully validate the diagnosis</p>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-fg-muted italic">No missing information gaps identified.</p>
            )}
          </div>
        </div>
      </div>
    </Section>
  );
}
