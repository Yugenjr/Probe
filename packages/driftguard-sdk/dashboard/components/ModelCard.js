import React from 'react';
import { useRouter } from 'next/router';
import { formatPercent } from '../lib/utils';
import { Layers3, GitBranch } from 'lucide-react';

const STATUS_CONFIG = {
  healthy:    { label: 'Healthy',    color: 'var(--green)' },
  degraded:   { label: 'Drifting',   color: 'var(--amber)' },
  retraining: { label: 'Retraining', color: 'var(--blue)' },
  failed:     { label: 'Failed',     color: 'var(--red)' },
};

export default function ModelCard({ model }) {
  const router = useRouter();
  const status = STATUS_CONFIG[model.status] || { label: model.status || 'Unknown', color: 'var(--text-muted)' };

  const accuracyVal = model.accuracy;
  const isNull = accuracyVal === null || accuracyVal === undefined;

  let features = [];
  try {
    features = typeof model.features === 'string' ? JSON.parse(model.features) : (Array.isArray(model.features) ? model.features : []);
  } catch { features = []; }

  return (
    <div
      onClick={() => router.push(`/models/${model.model_id}`)}
      className="bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg p-4 flex flex-col gap-4 cursor-pointer transition-all hover:border-[var(--border-hover)] hover:shadow-sm group"
    >
      {/* Header row */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-8 h-8 rounded-md bg-[var(--bg-base)] border border-[var(--border)] flex items-center justify-center shrink-0">
            <Layers3 size={14} className="text-[var(--text-secondary)] group-hover:text-[var(--text-primary)] transition-colors" />
          </div>
          <div className="min-w-0">
            <div className="text-[14px] font-semibold text-[var(--text-primary)] truncate tracking-tight">
              {model.model_id}
            </div>
            <div className="flex items-center gap-1.5 mt-0.5">
              <GitBranch size={10} className="text-[var(--text-muted)]" />
              <span className="text-[11px] text-[var(--text-secondary)] font-mono">
                {model.version ? `v${model.version}` : 'N/A'}
              </span>
            </div>
          </div>
        </div>

        {/* Status indicator */}
        <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-[var(--bg-base)] border border-[var(--border)] shrink-0">
          <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: status.color }} />
          <span className="text-[11px] font-medium text-[var(--text-secondary)]">
            {status.label}
          </span>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 gap-4 pt-4 border-t border-[var(--border)]">
        <div>
          <div className="text-[12px] text-[var(--text-secondary)] mb-1">Champion Accuracy</div>
          <div className={`text-[14px] font-mono font-medium ${isNull ? 'text-[var(--text-muted)]' : 'text-[var(--text-primary)]'}`}>
            {isNull ? 'N/A' : formatPercent(accuracyVal)}
          </div>
        </div>
        <div>
          <div className="text-[12px] text-[var(--text-secondary)] mb-1">Drift Threshold</div>
          <div className="text-[14px] font-mono font-medium text-[var(--text-primary)]">
            {model.drift_threshold != null ? model.drift_threshold.toFixed(2) : 'N/A'}
          </div>
        </div>
      </div>

      {/* Features */}
      {features.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-1">
          {features.slice(0, 3).map((feat, i) => (
            <span key={i} className="text-[11px] px-2 py-0.5 rounded bg-[var(--bg-base)] border border-[var(--border)] text-[var(--text-secondary)] font-mono truncate max-w-[100px]">
              {feat}
            </span>
          ))}
          {features.length > 3 && (
            <span className="text-[11px] px-1.5 py-0.5 text-[var(--text-muted)]">
              +{features.length - 3}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
