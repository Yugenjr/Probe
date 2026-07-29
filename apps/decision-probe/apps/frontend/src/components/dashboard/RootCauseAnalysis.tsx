import React from 'react';
import { SectionContainer } from '../layout/SectionContainer';
import { BlockRenderer } from '../workspace/BlockRenderer';

export function RootCauseAnalysis({ blocks }: { blocks: any[] }) {
  if (!blocks || blocks.length === 0) return null;
  
  return (
    <SectionContainer 
      title="Root Cause Analysis" 
      description="Metric anomalies, git changes, failure patterns, and agent reasoning."
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {blocks.map(block => (
          <BlockRenderer key={block.id} block={block} />
        ))}
      </div>
    </SectionContainer>
  );
}
