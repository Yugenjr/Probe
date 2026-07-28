"use client";

import React from 'react';
import { Section } from './BlockRenderer';

export interface CommitItem {
  hash: string;
  author: string;
  message: string;
  files_changed: string[];
}

export interface GitAnalysisBlockProps {
  block: {
    id: string;
    type: string;
    content: {
      commits?: CommitItem[];
    };
  };
}

export function GitAnalysisBlock({ block }: GitAnalysisBlockProps) {
  const content = block.content || {};
  const commits = content.commits || [];

  return (
    <Section title="Git Code Changes" count={commits.length}>
      <div className="mx-2 rounded-xl border border-border bg-panel/30 p-5 shadow-sm">
        {commits.length > 0 ? (
          <div className="space-y-4">
            {commits.map((commit, idx) => (
              <div key={idx} className="border border-border-subtle/50 bg-raised/10 rounded-xl p-4 text-[12.5px] space-y-3">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-2.5">
                  <div className="flex items-center gap-2">
                    <span className="bg-accent/15 text-accent border border-accent/25 text-micro font-bold px-2 py-0.5 rounded font-mono">
                      {commit.hash}
                    </span>
                    <span className="font-semibold text-foreground/90 leading-tight">
                      {commit.message}
                    </span>
                  </div>
                  <span className="text-fg-muted text-[11px] font-medium whitespace-nowrap">
                    Author: {commit.author}
                  </span>
                </div>
                
                {commit.files_changed.length > 0 && (
                  <div className="bg-raised/20 border border-border-subtle/25 rounded-xl p-3 space-y-1.5 font-mono text-[11px]">
                    <span className="text-micro text-fg-muted uppercase tracking-wider block font-sans font-medium mb-1">
                      Modified Files:
                    </span>
                    <ul className="space-y-1">
                      {commit.files_changed.map((file, i) => (
                        <li key={i} className="text-foreground/80 flex items-center gap-2">
                          <span className="text-accent">•</span>
                          <span>{file}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-[12.5px] text-fg-muted italic">No repository git change records found.</p>
        )}
      </div>
    </Section>
  );
}
