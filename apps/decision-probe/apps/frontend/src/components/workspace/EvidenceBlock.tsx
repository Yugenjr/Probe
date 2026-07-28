"use client";

import React from 'react';
import { Section } from './BlockRenderer';

export interface ExtractedEntity {
  name: string;
  type: string;
  confidence: number;
  source_chunk: string;
}

export interface EvidenceBlockProps {
  block: {
    id: string;
    type: string;
    content: {
      entities?: ExtractedEntity[];
    };
  };
}

export function EvidenceBlock({ block }: EvidenceBlockProps) {
  const entities = block.content?.entities || [];

  return (
    <Section title="Extracted Evidence Facts" count={entities.length}>
      {entities.length === 0 ? (
        <p className="text-[12.5px] text-fg-muted py-4 italic">No evidence entities extracted yet.</p>
      ) : (
        <div className="overflow-x-auto mt-2">
          <table className="w-full border-collapse text-[12.5px]">
            <thead>
              <tr className="border-b border-border-subtle text-fg-muted text-[11px] font-semibold text-left">
                <th className="pb-2 font-medium w-1/3">Entity Name</th>
                <th className="pb-2 font-medium">Type</th>
                <th className="pb-2 font-medium text-center">Confidence</th>
                <th className="pb-2 font-medium text-right">Source Chunk</th>
              </tr>
            </thead>
            <tbody>
              {entities.map((entity, idx) => {
                // Style type badges
                let badgeClass = "bg-background-soft text-fg-muted border-border-subtle";
                const typeLower = (entity.type || "unknown").toLowerCase();
                
                if (typeLower === "service") {
                  badgeClass = "bg-info/5 text-info border-info/10";
                } else if (typeLower === "database") {
                  badgeClass = "bg-warning/5 text-warning border-warning/10";
                } else if (typeLower === "component") {
                  badgeClass = "bg-success/5 text-success border-success/10";
                } else if (typeLower === "deployment") {
                  badgeClass = "bg-accent/5 text-accent border-accent/10";
                } else if (typeLower === "incident") {
                  badgeClass = "bg-danger/5 text-danger border-danger/10";
                } else if (typeLower === "api") {
                  badgeClass = "bg-primary/5 text-primary border-primary/10";
                } else if (typeLower === "user") {
                  badgeClass = "bg-accent/5 text-accent border-accent/10";
                }

                const confPercent = Math.round((entity.confidence || 0.95) * 100);

                return (
                  <tr key={idx} className="border-b border-border-subtle/40 last:border-0 hover:bg-raised/30 transition-colors">
                    <td className="py-2.5 font-medium text-foreground">{entity.name}</td>
                    <td className="py-2.5">
                      <span className={`mono rounded px-1.5 py-0.5 text-[10px] border ${badgeClass}`}>
                        {entity.type}
                      </span>
                    </td>
                    <td className="py-2.5 text-center">
                      <div className="flex items-center justify-center gap-2">
                        <div className="w-12 bg-border-subtle rounded-full h-1.5 overflow-hidden hidden sm:block">
                          <div 
                            className="bg-accent h-1.5 rounded-full" 
                            style={{ width: `${confPercent}%` }} 
                          />
                        </div>
                        <span className="mono font-semibold text-[11px]">{confPercent}%</span>
                      </div>
                    </td>
                    <td className="py-2.5 text-right">
                      <span className="mono text-[10px] bg-background border border-border-subtle px-1.5 py-0.5 rounded text-fg-muted font-medium">
                        {entity.source_chunk}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </Section>
  );
}
