import React from 'react';
import { SectionContainer } from '../layout/SectionContainer';
import { BlockRenderer } from '../workspace/BlockRenderer';

export function EvidenceIntelligence({ blocks }: { blocks: any[] }) {
  if (!blocks || blocks.length === 0) return null;
  
  return (
    <SectionContainer 
      title="Evidence Intelligence" 
      description="Gathered logs, external data, identified gaps, and visual charts."
    >
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {blocks.map(block => (
          <BlockRenderer key={block.id} block={block} />
        ))}
      </div>
    </SectionContainer>
  );
}
