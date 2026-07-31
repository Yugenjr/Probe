import React from 'react';

const CONFIG = {
  healthy:    { label: 'Healthy',    color: 'var(--green)', bg: 'var(--green-dim)' },
  degraded:   { label: 'Drifting',   color: 'var(--amber)', bg: 'var(--amber-dim)' },
  retraining: { label: 'Retraining', color: 'var(--blue)',  bg: 'var(--blue-dim)' },
  failed:     { label: 'Failed',     color: 'var(--red)',   bg: 'var(--red-dim)' },
  archived:   { label: 'Archived',   color: 'var(--text-secondary)', bg: 'var(--bg-base)' },
};

export default function StatusBadge({ status }) {
  const cfg = CONFIG[status] || { label: status || 'Unknown', color: 'var(--text-secondary)', bg: 'var(--bg-base)' };

  return (
    <span
      className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium border"
      style={{
        backgroundColor: cfg.bg,
        color: cfg.color,
        borderColor: cfg.bg === 'var(--bg-base)' ? 'var(--border)' : 'transparent'
      }}
    >
      <span className="w-1.5 h-1.5 rounded-full mr-1.5" style={{ backgroundColor: cfg.color }} />
      {cfg.label}
    </span>
  );
}
