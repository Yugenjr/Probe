import React from 'react';
import { Section } from './BlockRenderer';
import { Lightbulb } from 'lucide-react';

export function PreventiveRecommendationBlock({ block }: { block: any }) {
  const c = block.content || {};
  const recs = c.recommendations || [
    "Implement circuit breakers on the auth-service API calls.",
    "Increase pgbouncer max_client_conn threshold to 5000.",
    "Add caching layer for frequent read-only config queries."
  ];

  return (
    <Section title="Preventive Recommendations" defaultOpen={true}>
      <div className="px-4">
        <div className="bg-accent/5 border border-accent/20 rounded-lg p-3">
          <div className="flex items-center gap-2 text-accent font-semibold text-[13px] mb-3">
            <Lightbulb size={16} />
            <span>AI Suggested Next Steps</span>
          </div>
          <ul className="space-y-2">
            {recs.map((rec: string, i: number) => (
              <li key={i} className="flex items-start gap-2 text-[12.5px] text-foreground">
                <span className="mt-1 flex h-1.5 w-1.5 shrink-0 rounded-full bg-accent"></span>
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </Section>
  );
}
