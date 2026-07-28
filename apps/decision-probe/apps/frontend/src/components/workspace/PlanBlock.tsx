import React from 'react';
import { Section } from './BlockRenderer';

export interface PlanBlockProps {
  block: {
    id: string;
    type: string;
    order: number;
    content: {
      objectives?: string[];
      questions?: string[];
      evidence_needed?: string[];
      priority?: string;
    };
  };
}

export function PlanBlock({ block }: PlanBlockProps) {
  const { objectives = [], questions = [], evidence_needed = [], priority = 'medium' } = block.content || {};

  const getPriorityBadgeClass = (level: string) => {
    switch (level.toLowerCase()) {
      case 'high':
        return 'bg-danger/10 text-danger border-danger/20';
      case 'medium':
        return 'bg-warning/10 text-warning border-warning/20';
      case 'low':
      default:
        return 'bg-info/10 text-info border-info/20';
    }
  };

  return (
    <Section 
      title="Investigation Plan" 
      action={
        <span className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider border ${getPriorityBadgeClass(priority)}`}>
          Priority: {priority}
        </span>
      }
    >
      <div className="rounded-xl border border-border bg-panel p-5 space-y-5 shadow-sm">
        {/* Objectives Section */}
        {objectives.length > 0 && (
          <div className="space-y-2">
            <h3 className="text-[13px] font-semibold text-fg-strong tracking-wide uppercase text-xs">Objectives</h3>
            <ul className="space-y-1.5 pl-1">
              {objectives.map((obj, i) => (
                <li key={i} className="flex items-start gap-2.5 text-[12.5px] text-foreground leading-relaxed">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-accent" />
                  <span>{obj}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Questions Section */}
        {questions.length > 0 && (
          <div className="space-y-2">
            <h3 className="text-[13px] font-semibold text-fg-strong tracking-wide uppercase text-xs">Questions to Answer</h3>
            <ul className="space-y-1.5 pl-1">
              {questions.map((q, i) => (
                <li key={i} className="flex items-start gap-2.5 text-[12.5px] text-foreground leading-relaxed">
                  <span className="mt-1.5 text-accent font-mono text-[10px] shrink-0 font-bold">?</span>
                  <span>{q}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Evidence Needed Section */}
        {evidence_needed.length > 0 && (
          <div className="space-y-2">
            <h3 className="text-[13px] font-semibold text-fg-strong tracking-wide uppercase text-xs">Evidence Needed</h3>
            <ul className="space-y-1.5 pl-1">
              {evidence_needed.map((ev, i) => (
                <li key={i} className="flex items-start gap-2.5 text-[12.5px] text-fg-muted leading-relaxed">
                  <span className="mt-1.5 text-warning shrink-0 text-[10px]">☐</span>
                  <span>{ev}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </Section>
  );
}
