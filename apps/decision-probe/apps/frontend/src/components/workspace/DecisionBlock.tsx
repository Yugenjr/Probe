import React from 'react';
import { Section } from './BlockRenderer';

export interface DecisionBlockProps {
  block: any;
}

export function DecisionBlock({ block }: DecisionBlockProps) {
  const c = block.content || {};

  const confValue = c.Confidence;
  const confDisplay = typeof confValue === 'number' 
    ? (confValue > 1 ? (confValue / 100).toFixed(2) : confValue.toFixed(2))
    : confValue;

  const riskLevel = c['Risk Level'] || c.Risk || 'Unknown';
  const riskColor = (() => {
    const l = riskLevel?.toLowerCase?.();
    if (l === 'high' || l === 'critical') return 'bg-danger';
    if (l === 'medium') return 'bg-warning';
    return 'bg-success';
  })();

  return (
    <Section title="Decision">
      <div className="mx-4 rounded border border-border-subtle bg-raised/20 p-4">
        {/* Header Row */}
        <div className="flex items-start justify-between gap-4 mb-4 pb-4 border-b border-border-subtle">
          <div>
            <div className="text-micro text-fg-muted mb-1">Status</div>
            <div className="text-[13px] font-medium text-info flex items-center gap-1.5">
              <span className="relative flex h-2 w-2"><span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-info opacity-50" /><span className="relative inline-flex h-2 w-2 rounded-full bg-info" /></span>
              Analysis Complete
            </div>
          </div>
          <div>
            <div className="text-micro text-fg-muted mb-1">Confidence</div>
            <div className="text-[14px] font-mono text-accent">{(Number(confDisplay || 0.85) * 100).toFixed(0)}%</div>
          </div>
          <div>
            <div className="text-micro text-fg-muted mb-1">Risk Level</div>
            <div className="text-[13px] text-foreground flex items-center gap-1.5">
              <span className={`h-1.5 w-1.5 rounded-full ${riskColor}`} />
              {riskLevel}
            </div>
          </div>
        </div>

        {/* Root Cause Hypothesis */}
        <div className="mb-4">
          <div className="text-micro text-fg-muted mb-1.5">Root Cause Hypothesis</div>
          <div className="text-[13px] text-foreground leading-relaxed">
            {c.Decision || c.Reasoning || c.text || 'Pending analysis...'}
          </div>
        </div>

        {/* Evidence & Gaps */}
        <div className="grid grid-cols-2 gap-6 mb-4">
          <div>
            <div className="text-micro text-fg-muted mb-1.5">Supporting Evidence</div>
            <ul className="text-[12px] text-fg-muted space-y-1">
              {(c['Supporting Evidence'] ? (Array.isArray(c['Supporting Evidence']) ? c['Supporting Evidence'] : [c['Supporting Evidence']]) : ['Logs indicate connection pool exhaustion']).map((ev: string, i: number) => (
                <li key={i} className="flex items-start gap-1.5">
                  <span className="text-accent mt-0.5">✓</span> {ev}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <div className="text-micro text-fg-muted mb-1.5">Missing Evidence</div>
            <ul className="text-[12px] text-warning/80 space-y-1">
              {(c['Missing Information'] ? (Array.isArray(c['Missing Information']) ? c['Missing Information'] : [c['Missing Information']]) : ['No network trace available']).map((info: string, i: number) => (
                <li key={i} className="flex items-start gap-1.5">
                  <span className="text-warning mt-0.5">?</span> {info}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Alternatives */}
        {c['Alternative Actions'] && (
          <div className="mb-4">
            <div className="text-micro text-fg-muted mb-1.5">Alternative Hypotheses</div>
            <div className="text-[12px] text-fg-muted space-y-1">
              {(Array.isArray(c['Alternative Actions']) ? c['Alternative Actions'] : [c['Alternative Actions']]).map((alt: string, i: number) => (
                <div key={i} className="flex items-start gap-2">
                  <span className="opacity-50 mt-0.5">–</span> {alt}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Next step */}
        {c['Recommended Next Step'] && (
          <div className="pt-4 border-t border-border-subtle mt-2">
            <div className="text-micro text-fg-muted mb-2">Recommended Next Action</div>
            <button className="flex h-7 items-center gap-2 rounded border border-accent/40 bg-accent/10 px-3 text-[12px] font-medium text-accent hover:bg-accent/20 transition-colors">
              <span className="mono">▶</span> {c['Recommended Next Step']}
            </button>
          </div>
        )}
      </div>
    </Section>
  );
}
