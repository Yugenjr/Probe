"use client";

import React from 'react';
import { Section } from './BlockRenderer';

export interface CriticReview {
  hypothesis_id: string;
  strengths: string[];
  weaknesses: string[];
  missing_information: string[];
  confidence_adjustment: number;
}

export interface CriticBlockProps {
  block: {
    id: string;
    type: string;
    content: {
      reviews: CriticReview[];
    };
  };
}

export function CriticBlock({ block }: CriticBlockProps) {
  const reviews = block.content?.reviews || [];

  return (
    <Section title="Critic Hypothesis Analysis" count={reviews.length}>
      {reviews.length === 0 ? (
        <p className="text-[12.5px] text-fg-muted py-4 italic">No hypothesis reviews generated yet.</p>
      ) : (
        <div className="space-y-6 mt-2">
          {reviews.map((review, idx) => {
            const adj = review.confidence_adjustment || 0.0;
            const adjSign = adj >= 0 ? "+" : "";
            const adjColor = adj >= 0 ? "text-success bg-success/5 border-success/10" : "text-danger bg-danger/5 border-danger/10";
            
            return (
              <div key={idx} className="border border-border/80 bg-raised/10 hover:bg-raised/20 transition-all rounded-xl p-5 shadow-sm">
                {/* Header */}
                <div className="flex items-center justify-between gap-3 mb-4 pb-3 border-b border-border-subtle/50">
                  <div className="flex items-center gap-2">
                    <span className="mono text-[10px] text-fg-muted font-bold tracking-wide uppercase bg-raised px-1.5 py-0.5 rounded">
                      Critique for {review.hypothesis_id}
                    </span>
                  </div>
                  <span className={`mono text-[11px] font-semibold border rounded-full px-2 py-0.5 ${adjColor}`}>
                    Confidence Adj: {adjSign}{(adj * 100).toFixed(0)}%
                  </span>
                </div>

                {/* Analysis Columns */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-[12px]">
                  {/* Strengths */}
                  <div>
                    <span className="text-micro text-success font-semibold tracking-wider uppercase block mb-2">
                      Strengths / Supporting
                    </span>
                    {review.strengths && review.strengths.length > 0 ? (
                      <ul className="space-y-1.5 text-foreground/80">
                        {review.strengths.map((str, i) => (
                          <li key={i} className="flex items-start gap-1.5 leading-snug">
                            <span className="text-success select-none">✓</span>
                            <span>{str}</span>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-fg-muted italic">No distinct strengths identified.</p>
                    )}
                  </div>

                  {/* Weaknesses */}
                  <div>
                    <span className="text-micro text-danger font-semibold tracking-wider uppercase block mb-2">
                      Weaknesses / Gaps
                    </span>
                    {review.weaknesses && review.weaknesses.length > 0 ? (
                      <ul className="space-y-1.5 text-foreground/80">
                        {review.weaknesses.map((wk, i) => (
                          <li key={i} className="flex items-start gap-1.5 leading-snug">
                            <span className="text-danger select-none">✗</span>
                            <span>{wk}</span>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-fg-muted italic">No distinct weaknesses identified.</p>
                    )}
                  </div>

                  {/* Missing Information */}
                  <div>
                    <span className="text-micro text-warning font-semibold tracking-wider uppercase block mb-2">
                      Missing Information
                    </span>
                    {review.missing_information && review.missing_information.length > 0 ? (
                      <ul className="space-y-1.5 text-foreground/80">
                        {review.missing_information.map((miss, i) => (
                          <li key={i} className="flex items-start gap-1.5 leading-snug">
                            <span className="text-warning font-bold select-none">?</span>
                            <span>{miss}</span>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-fg-muted italic">No missing information noted.</p>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </Section>
  );
}
