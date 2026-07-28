"use client";

import React from 'react';
import { Section } from './BlockRenderer';

export interface KnowledgeBlockProps {
  block: {
    id: string;
    type: string;
    content: {
      problem?: string;
      solution?: string;
      prevention?: string;
    };
  };
}

export function KnowledgeBlock({ block }: KnowledgeBlockProps) {
  const content = block.content || {};
  const problem = content.problem || "";
  const solution = content.solution || "";
  const prevention = content.prevention || "";

  return (
    <Section title="Incident Knowledge Storage">
      <div className="mx-2 rounded-xl border border-border bg-panel/30 p-5 shadow-sm space-y-4 text-[12.5px]">
        {/* Problem Card */}
        <div className="border border-border-subtle/50 bg-raised/10 rounded-xl p-4 space-y-1.5">
          <strong className="text-micro text-danger font-semibold tracking-wider uppercase block">
            Aggregated Problem Context:
          </strong>
          <p className="text-foreground/90 leading-relaxed font-medium">
            {problem}
          </p>
        </div>

        {/* Solution Card */}
        <div className="border border-border-subtle/50 bg-raised/10 rounded-xl p-4 space-y-1.5">
          <strong className="text-micro text-success font-semibold tracking-wider uppercase block">
            Applied Engineering Solution:
          </strong>
          <p className="text-foreground/90 leading-relaxed">
            {solution}
          </p>
        </div>

        {/* Prevention Card */}
        <div className="border border-border-subtle/50 bg-raised/10 rounded-xl p-4 space-y-1.5">
          <strong className="text-micro text-accent font-semibold tracking-wider uppercase block">
            Prevention Alerting Safeguards:
          </strong>
          <p className="text-foreground/90 leading-relaxed">
            {prevention}
          </p>
        </div>
      </div>
    </Section>
  );
}
