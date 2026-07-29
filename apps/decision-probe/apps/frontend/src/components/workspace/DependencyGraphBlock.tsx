import React from 'react';
import { Section } from './BlockRenderer';
import { Network } from 'lucide-react';

export function DependencyGraphBlock({ block }: { block: any }) {
  // In a real scenario, this would render an interactive D3/vis.js graph of dependencies
  return (
    <Section title="Impact Radius" defaultOpen={true}>
      <div className="px-4">
        <div className="h-[200px] w-full rounded-lg border border-border-subtle bg-raised/30 flex flex-col items-center justify-center relative overflow-hidden">
          {/* Abstract representation of a graph */}
          <div className="absolute inset-0 opacity-10 bg-[radial-gradient(circle_at_center,var(--color-accent)_1px,transparent_1px)]" style={{ backgroundSize: '20px 20px' }}></div>
          
          <Network size={32} className="text-accent mb-3 opacity-80" />
          <div className="text-[13px] font-semibold text-foreground z-10">Dependency Graph Generated</div>
          <div className="text-[11px] text-fg-muted mt-1 z-10 text-center max-w-[80%]">
            Visualizing 14 downstream services affected by the current database degradation.
          </div>
          
          <button className="mt-4 z-10 text-[11px] font-medium bg-background border border-border px-3 py-1.5 rounded shadow-sm hover:bg-raised transition-colors">
            Expand Interactive View
          </button>
        </div>
      </div>
    </Section>
  );
}
