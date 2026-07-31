import React from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, CartesianGrid } from 'recharts';

const formatDriftScore = (score) => {
  return score !== null && score !== undefined ? score.toFixed(4) : 'N/A';
};

export default function DriftChart({ data, threshold }) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-[var(--bg-surface)] border border-[var(--border)] h-[350px] rounded-lg flex items-center justify-center text-[var(--text-muted)] text-[13px]">
        No predictions recorded yet
      </div>
    );
  }

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      const dateStr = new Date(item.timestamp).toLocaleString();
      return (
        <div className="bg-[var(--bg-surface)] border border-[var(--border)] p-3 rounded-md shadow-sm">
          <p className="text-[10px] text-[var(--text-muted)] font-medium uppercase tracking-widest mb-1">Telemetry Record</p>
          <p className="font-medium text-[12px] text-[var(--text-primary)] mb-1">Time: {dateStr}</p>
          <p className="font-medium text-[12px] text-[var(--text-primary)]">Drift Score: {formatDriftScore(item.drift_score)}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-[var(--bg-surface)] border border-[var(--border)] p-4 rounded-lg flex flex-col gap-3">
      <div className="flex justify-between items-center">
        <h3 className="text-[14px] font-semibold text-[var(--text-primary)]">Drift Score Timeline</h3>
        <span className="text-[11px] font-medium text-[var(--text-secondary)] bg-[var(--bg-base)] border border-[var(--border)] px-2 py-0.5 rounded">
          SLA Limit: {threshold}
        </span>
      </div>
      <div className="h-[300px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="driftGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--text-primary)" stopOpacity={0.1}/>
                <stop offset="95%" stopColor="var(--text-primary)" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false} />
            <XAxis 
              dataKey="timestamp" 
              tickFormatter={(t) => new Date(t).toLocaleTimeString()}
              stroke="var(--text-muted)"
              fontSize={10}
              tickMargin={10}
              axisLine={{ stroke: 'var(--border)' }}
            />
            <YAxis 
              stroke="var(--text-muted)"
              fontSize={10}
              tickMargin={10}
              axisLine={{ stroke: 'var(--border)' }}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ stroke: 'var(--border)', strokeWidth: 1 }} />
            
            {threshold && (
              <ReferenceLine 
                y={threshold} 
                stroke="var(--red)" 
                strokeDasharray="4 4"
                label={{ 
                  position: 'insideTopLeft', 
                  value: 'THRESHOLD', 
                  fill: 'var(--red)',
                  fontSize: 10, 
                  fontWeight: 600 
                }} 
              />
            )}

            <Area 
              type="monotone" 
              dataKey="drift_score" 
              stroke="var(--text-primary)" 
              strokeWidth={1.5}
              fillOpacity={1} 
              fill="url(#driftGradient)" 
              activeDot={{ r: 4, strokeWidth: 0, fill: 'var(--text-primary)' }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
