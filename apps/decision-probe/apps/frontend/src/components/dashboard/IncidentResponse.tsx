import React from 'react';
import { SectionContainer } from '../layout/SectionContainer';
import { BlockRenderer } from '../workspace/BlockRenderer';

export function IncidentResponse({ blocks }: { blocks: any[] }) {
  if (!blocks || blocks.length === 0) return null;
  
  return (
    <SectionContainer 
      title="Incident Response" 
      description="Remediation steps, response plans, timeline, and knowledge base integration."
    >
      <div className="flex flex-col gap-4">
        {blocks.map(block => (
          <BlockRenderer key={block.id} block={block} />
        ))}
      </div>
    </SectionContainer>
  );
}
