import React, { useState } from 'react';
import { formatDate, formatPercent } from '../lib/utils';
import StatusBadge from './StatusBadge';

export default function RetrainingHistory({ events }) {
  const [showAll, setShowAll] = useState(false);

  if (!events || events.length === 0) {
    return (
      <div className="bg-[var(--bg-surface)] border border-[var(--border)] p-6 rounded-lg text-center text-[var(--text-muted)] text-[13px]">
        No retraining events recorded yet
      </div>
    );
  }

  const sortedEvents = [...events].sort((a, b) => new Date(b.start_time) - new Date(a.start_time));
  const displayedEvents = showAll ? sortedEvents : sortedEvents.slice(0, 10);
  const hasMore = sortedEvents.length > 10;

  const getDotColor = (status) => {
    switch (String(status).toLowerCase()) {
      case 'completed': return 'bg-[var(--text-primary)]';
      case 'running': return 'bg-[var(--blue)] animate-pulse';
      case 'failed': return 'bg-[var(--red)]';
      default: return 'bg-[var(--text-muted)]';
    }
  };

  const renderAccuracyChange = (event) => {
    if (
      event.status !== 'completed' ||
      event.old_accuracy == null ||
      event.new_accuracy == null
    ) {
      return null;
    }
    const diff = event.new_accuracy - event.old_accuracy;
    const percentChange = (diff * 100).toFixed(1);
    
    return (
      <div className="mt-2 text-[12px] font-mono text-[var(--text-secondary)]">
        v{event.old_version} → v{event.new_version} | {formatPercent(event.old_accuracy)} → {formatPercent(event.new_accuracy)} 
        <span className="ml-2 font-medium text-[var(--text-primary)]">
          ({diff > 0 ? '+' : ''}{percentChange}%)
        </span>
      </div>
    );
  };

  return (
    <div className="bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg flex flex-col">
      <div className="px-5 py-3 border-b border-[var(--border)]">
        <h3 className="text-[14px] font-semibold text-[var(--text-primary)]">Retraining History</h3>
      </div>

      <div className="p-5">
        <div className="relative pl-4 border-l border-[var(--border)] space-y-5">
          {displayedEvents.map((ev, idx) => (
            <div key={ev.id || idx} className="relative">
              <div className={`absolute -left-[21px] top-1.5 w-2 h-2 rounded-full ${getDotColor(ev.status)} ring-4 ring-[var(--bg-surface)]`} />

              <div className="space-y-1">
                <div className="flex items-center gap-3">
                  <span className="text-[11px] text-[var(--text-muted)] font-mono">
                    {formatDate(ev.start_time)}
                  </span>
                  <StatusBadge status={ev.status} />
                  {ev.triggered_by === 'manual' && (
                    <span className="text-[10px] text-[var(--text-secondary)] bg-[var(--bg-base)] px-1.5 py-0.5 rounded border border-[var(--border)]">
                      Manual
                    </span>
                  )}
                </div>
                
                <p className="text-[13px] text-[var(--text-primary)] leading-relaxed pt-1">
                  {ev.status === 'completed'
                    ? 'Retraining pipeline completed successfully.'
                    : ev.status === 'running'
                    ? 'Retraining flow is currently executing.'
                    : ev.details?.message || ev.error || 'Retraining event failed.'}
                </p>
                {renderAccuracyChange(ev)}
              </div>
            </div>
          ))}
        </div>

        {hasMore && (
          <button
            onClick={() => setShowAll(!showAll)}
            className="w-full mt-6 py-2 rounded-md border border-[var(--border)] text-[13px] font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:border-[var(--border-hover)] transition-colors"
          >
            {showAll ? 'Show Less' : `View All (${events.length})`}
          </button>
        )}
      </div>
    </div>
  );
}
