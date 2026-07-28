import React from 'react';
import { Section } from './BlockRenderer';

export interface IncidentBlockProps {
  block: any;
}

export function IncidentBlock({ block }: IncidentBlockProps) {
  const c = block.content || {};

  const fields: [string, string][] = [];
  if (c.title) fields.push(["Title", c.title]);
  if (c.description) fields.push(["Description", c.description]);
  if (c.severity) fields.push(["Severity", c.severity]);
  if (c.status) fields.push(["Status", c.status]);
  if (c.affected_systems) {
    const systems = Array.isArray(c.affected_systems) ? c.affected_systems.join(', ') : c.affected_systems;
    fields.push(["Affected", systems]);
  }
  if (c.region) fields.push(["Region", c.region]);
  if (c.started) fields.push(["Started", c.started]);
  if (c.reporter) fields.push(["Reporter", c.reporter]);

  return (
    <Section title="Incident">
      <dl className="grid grid-cols-[140px_1fr] gap-x-6 gap-y-2.5 text-[13px] pl-4">
        {fields.map(([k, v]) => (
          <div key={k} className="contents">
            <dt className="text-fg-muted">{k}</dt>
            <dd className="text-foreground">{v}</dd>
          </div>
        ))}
      </dl>
    </Section>
  );
}
