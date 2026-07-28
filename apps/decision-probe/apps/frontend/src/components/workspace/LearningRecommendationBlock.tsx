"use client";

import React from 'react';
import { Section } from './BlockRenderer';

export interface RecommendationItem {
  type: "investigation" | "prevention" | string;
  suggestion: string;
}

export interface LearningRecommendationBlockProps {
  block: {
    id: string;
    type: string;
    content: {
      recommendations?: RecommendationItem[];
    };
  };
}

export function LearningRecommendationBlock({ block }: LearningRecommendationBlockProps) {
  const content = block.content || {};
  const recommendations = content.recommendations || [];

  const typeBadge = (type: string) => {
    const base = "text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ";
    if (type.toLowerCase() === "investigation") {
      return <span className={base + "bg-blue-500/10 text-blue-400 border-blue-500/20"}>Investigation Advice</span>;
    }
    return <span className={base + "bg-green-500/10 text-green-400 border-green-500/20"}>Prevention Advice</span>;
  };

  return (
    <Section title="AI Learning & RAG Recommendations" count={recommendations.length}>
      <div className="mx-2 rounded-xl border border-border bg-panel/30 p-5 shadow-sm">
        {recommendations.length > 0 ? (
          <div className="space-y-3.5 text-[12.5px]">
            {recommendations.map((item, idx) => (
              <div key={idx} className="flex items-start justify-between gap-4 border border-border-subtle/50 bg-raised/10 rounded-xl p-4">
                <div className="space-y-1.5 flex-1">
                  <p className="font-semibold text-foreground leading-relaxed">
                    {item.suggestion}
                  </p>
                  <div>
                    {typeBadge(item.type)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-[12.5px] text-fg-muted italic">No recommendations extracted from learning process.</p>
        )}
      </div>
    </Section>
  );
}
