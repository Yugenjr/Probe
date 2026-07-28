"use client";

import React from 'react';
import { Section } from './BlockRenderer';

export interface MetricItem {
  name: string;
  value: number;
  timestamp: string;
}

export interface MetricAnalysisBlockProps {
  block: {
    id: string;
    type: string;
    content: {
      metrics?: MetricItem[];
    };
  };
}

export function MetricAnalysisBlock({ block }: MetricAnalysisBlockProps) {
  const content = block.content || {};
  const metrics = content.metrics || [];

  const metricLabel = (name: string) => {
    return name.replace(/_/g, " ").toUpperCase();
  };

  const metricFormatValue = (name: string, val: number) => {
    if (name.includes("connections") || name.includes("rate")) {
      return `${Math.round(val)}`;
    }
    if (name.includes("latency")) {
      return `${Math.round(val)}ms`;
    }
    return `${Math.round(val)}%`;
  };

  // Helper to color metrics progress bar
  const metricColor = (name: string, value: number) => {
    if (name.includes("cpu") || name.includes("connections") || name.includes("latency")) {
      if (value > 90) return "bg-danger";
      if (value > 75) return "bg-warning";
    }
    return "bg-success";
  };

  return (
    <Section title="Metric Analysis" count={metrics.length}>
      <div className="mx-2 rounded-xl border border-border bg-panel/30 p-5 shadow-sm">
        {metrics.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 text-[12.5px]">
            {metrics.map((item, idx) => (
              <div key={idx} className="border border-border-subtle/50 bg-raised/10 rounded-xl p-4 space-y-2.5">
                <div className="flex items-center justify-between font-semibold">
                  <span className="text-foreground/90">{metricLabel(item.name)}</span>
                  <span className="text-foreground">{metricFormatValue(item.name, item.value)}</span>
                </div>
                
                {/* Simulated utilization bar */}
                {(item.name.includes("usage") || item.name.includes("connections")) && (
                  <div className="w-full bg-border-subtle/30 h-2.5 rounded-full overflow-hidden">
                    <div 
                      className={`h-full rounded-full transition-all duration-500 ${metricColor(item.name, item.value)}`}
                      style={{ width: `${Math.min(100, item.value)}%` }}
                    />
                  </div>
                )}
                
                <div className="flex items-center justify-between text-[10px] text-fg-muted">
                  <span>Target: payments-db</span>
                  <span>Captured: {item.timestamp}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-[12.5px] text-fg-muted italic">No external observability metrics collected.</p>
        )}
      </div>
    </Section>
  );
}
