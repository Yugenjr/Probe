import React from 'react';
import { Server, CheckCircle2, TrendingUp, RotateCcw } from 'lucide-react';

const CONFIGS = {
  'Fleet Monitored':        { icon: Server,        color: 'var(--text-primary)',   bg: 'var(--bg-base)' },
  'Stable Champion Models': { icon: CheckCircle2,  color: 'var(--green)',          bg: 'var(--bg-base)' },
  'Drifting (SLA Breach)':  { icon: TrendingUp,    color: 'var(--amber)',          bg: 'var(--bg-base)' },
  'Active Retraining Loops':{ icon: RotateCcw,     color: 'var(--blue)',           bg: 'var(--bg-base)' },
};

export default function StatCard({ label, value }) {
  const cfg = CONFIGS[label] || CONFIGS['Fleet Monitored'];
  const Icon = cfg.icon;

  return (
    <div className="bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg p-5 flex flex-col justify-between transition-shadow hover:shadow-sm">
      <div className="flex items-center gap-2 mb-4">
        <div className={`w-6 h-6 rounded flex items-center justify-center bg-[${cfg.bg}]`}>
          <Icon size={14} color={cfg.color} strokeWidth={2} />
        </div>
        <span className="text-[13px] font-medium text-[var(--text-secondary)]">
          {label}
        </span>
      </div>
      <div className="flex items-baseline gap-2">
        <span className="text-3xl font-semibold tracking-tight text-[var(--text-primary)] leading-none">
          {value}
        </span>
      </div>
    </div>
  );
}
