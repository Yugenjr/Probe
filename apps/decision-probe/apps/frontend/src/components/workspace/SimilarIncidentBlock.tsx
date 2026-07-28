"use client";

import React from 'react';
import { Section } from './BlockRenderer';

export interface SimilarIncident {
  incident_id: string;
  similarity_score: number;
  root_cause: string;
  solution: str;
}

export interface SimilarIncidentBlockProps {
  block: {
    id: string;
    type: string;
    content: {
      similar_incidents?: SimilarIncident[];
    };
  };
}

export function SimilarIncidentBlock({ block }: SimilarIncidentBlockProps) {
  const content = block.content || {};
  const incidents = content.similar_incidents || [];

  return (
    <Section title="Similar Historical Incidents" count={incidents.length}>
      <div className="mx-2 rounded-xl border border-border bg-panel/30 p-5 shadow-sm">
        {incidents.length > 0 ? (
          <div className="space-y-4">
            {incidents.map((inc, idx) => (
              <div key={idx} className="border border-border-subtle/50 bg-raised/10 rounded-xl p-4 space-y-3 text-[12.5px]">
                <div className="flex items-center justify-between border-b border-border-subtle/30 pb-2">
                  <span className="font-mono font-bold text-accent">{inc.incident_id}</span>
                  <span className="bg-success/15 text-success border border-success/30 font-bold px-2 py-0.5 rounded text-[11px]">
                    {Math.round(inc.similarity_score * 100)}% Similarity
                  </span>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-1.5">
                  <div>
                    <strong className="text-fg-muted font-medium text-micro uppercase tracking-wider block mb-1">Previous Root Cause:</strong>
                    <p className="font-semibold text-foreground">{inc.root_cause}</p>
                  </div>
                  <div>
                    <strong className="text-fg-muted font-medium text-micro uppercase tracking-wider block mb-1">Previous Applied Fix:</strong>
                    <p className="text-foreground/90">{inc.solution}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-[12.5px] text-fg-muted italic">No matching historical incidents isolated.</p>
        )}
      </div>
    </Section>
  );
}
