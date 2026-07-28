"use client";

import React from 'react';
import { Section } from './BlockRenderer';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

export interface ChartBlockProps {
  block: any;
}

export function ChartBlock({ block }: ChartBlockProps) {
  const c = block.content || {};
  const data = c.data || [];

  return (
    <Section title="Metrics" count={data.length}>
      <div className="px-4">
        <div className="h-[160px] w-full text-[10px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 4, right: 12, left: 0, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-subtle)" />
              <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: 'var(--muted-foreground)', fontSize: 10 }} />
              <YAxis axisLine={false} tickLine={false} tick={{ fill: 'var(--muted-foreground)', fontSize: 10 }} />
              <Tooltip
                contentStyle={{ backgroundColor: 'var(--overlay)', borderColor: 'var(--border)', borderRadius: '4px', color: 'var(--foreground)', fontSize: 11 }}
                itemStyle={{ color: 'var(--accent)' }}
              />
              <Line type="monotone" dataKey="value" stroke="var(--accent)" strokeWidth={1.5} dot={false} activeDot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        {c.data_source && (
          <div className="mt-2 mono text-[10.5px] text-fg-muted">Source: {c.data_source}</div>
        )}
      </div>
    </Section>
  );
}
