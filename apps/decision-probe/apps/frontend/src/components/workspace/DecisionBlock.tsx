"use client";

import React from 'react';
import { Section } from './BlockRenderer';

export interface RootCause {
  title: string;
  description: string;
  confidence: number;
  supporting_chunks: string[];
}

export interface AlternativeHypothesis {
  title: string;
  description: string;
  confidence: number;
  supporting_chunks: string[];
}

export interface DecisionBlockProps {
  block: {
    id: string;
    type: string;
    content: {
      root_cause: RootCause;
      alternatives: AlternativeHypothesis[];
      reasoning: string;
    };
  };
}

export function DecisionBlock({ block }: DecisionBlockProps) {
  const content = block.content || {};
  const rootCause = content.root_cause || { title: "Pending Decisions", description: "Root cause analysis has not been completed.", confidence: 0, supporting_chunks: [] };
  const alternatives = content.alternatives || [];
  const reasoning = content.reasoning || "";

  const confPercent = Math.round((rootCause.confidence || 0) * 100);

  // Style tags based on confidence
  let badgeColor = "bg-background-soft text-fg-muted border-border-subtle";
  let ringColor = "ring-border-subtle/10";
  
  if (confPercent >= 70) {
    badgeColor = "bg-success/5 border-success/10 text-success";
    ringColor = "ring-success/15";
  } else if (confPercent >= 40) {
    badgeColor = "bg-warning/5 border-warning/10 text-warning";
    ringColor = "ring-warning/15";
  } else if (confPercent > 0) {
    badgeColor = "bg-danger/5 border-danger/10 text-danger";
    ringColor = "ring-danger/15";
  }

  return (
    <Section title="Root Cause Decision">
      <div className="mx-2 rounded-xl border border-border bg-panel/30 p-6 shadow-sm">
        {/* Top summary cards */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-5 mb-5 border-b border-border-subtle">
          <div>
            <span className="text-micro text-fg-muted uppercase tracking-wider block mb-1">Investigation Status</span>
            <div className="text-[13px] font-semibold text-accent flex items-center gap-1.5">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-accent opacity-65" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-accent" />
              </span>
              Root Cause Resolved
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div>
              <span className="text-micro text-fg-muted uppercase tracking-wider block mb-1 text-right">Winning Confidence</span>
              <span className={`mono text-[14px] font-bold border rounded-full px-2.5 py-0.5 ${badgeColor} ring-4 ${ringColor}`}>
                {confPercent}%
              </span>
            </div>
          </div>
        </div>

        {/* Selected Root Cause Details */}
        <div className="mb-6">
          <span className="text-micro text-fg-muted uppercase tracking-wider block mb-1.5">Selected Root Cause</span>
          <h3 className="text-[15px] font-bold text-fg-strong mb-1 leading-snug">
            {rootCause.title}
          </h3>
          <p className="text-[13px] text-foreground/80 leading-relaxed max-w-3xl mt-1.5">
            {rootCause.description}
          </p>

          {/* Supporting Chunks */}
          {rootCause.supporting_chunks && rootCause.supporting_chunks.length > 0 && (
            <div className="mt-3 flex flex-wrap items-center gap-1.5 text-[11px]">
              <span className="text-fg-muted font-medium">Supporting Evidence:</span>
              {rootCause.supporting_chunks.map((chk, idx) => (
                <span key={idx} className="mono text-[10px] bg-background border border-border-subtle px-1.5 py-0.5 rounded text-accent font-semibold">
                  {chk}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Reasoning explanation */}
        {reasoning && (
          <div className="mb-6 bg-raised/20 border border-border-subtle/50 rounded-xl p-4 text-[12.5px] leading-relaxed">
            <span className="text-micro text-fg-muted uppercase tracking-wider block mb-1.5">Decision Logic Summary</span>
            <p className="text-foreground/90">{reasoning}</p>
          </div>
        )}

        {/* Alternatives */}
        {alternatives.length > 0 && (
          <div className="pt-4 border-t border-border-subtle/50 mt-4">
            <span className="text-micro text-fg-muted uppercase tracking-wider block mb-2.5">Alternative Hypotheses Evaluated</span>
            <div className="space-y-3">
              {alternatives.map((alt, idx) => (
                <div key={idx} className="flex items-start justify-between gap-4 p-3 border border-border-subtle bg-background/30 rounded-lg hover:bg-background/55 transition-colors">
                  <div className="min-w-0 flex-1">
                    <h4 className="text-[12.5px] font-semibold text-foreground leading-snug">{alt.title}</h4>
                    <p className="text-[11.5px] text-fg-muted mt-1 leading-normal max-w-2xl">{alt.description}</p>
                  </div>
                  <span className="mono text-[11px] font-medium bg-background border border-border-subtle px-2 py-0.5 rounded shrink-0">
                    {Math.round((alt.confidence || 0) * 100)}% Conf.
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Section>
  );
}
