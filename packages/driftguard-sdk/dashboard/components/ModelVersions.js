import React from 'react';
import { formatPercent } from '../lib/utils';
import { RefreshCw } from 'lucide-react';

export default function ModelVersions({ versions, onRollback }) {
  if (!versions || versions.length === 0) {
    return (
      <div className="bg-[var(--bg-surface)] border border-[var(--border)] p-6 rounded-lg text-center text-[var(--text-muted)] text-[13px]">
        No versions registered in registry
      </div>
    );
  }

  const formatStatus = (status) => {
    return String(status).replace('_', ' ').toUpperCase();
  };

  return (
    <div className="bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg flex flex-col">
      <div className="px-5 py-3 border-b border-[var(--border)]">
        <h3 className="text-[14px] font-semibold text-[var(--text-primary)]">Model Registry</h3>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-[var(--bg-base)] border-b border-[var(--border)] text-[11px] text-[var(--text-secondary)] font-medium">
              <th className="px-5 py-2">Version</th>
              <th className="px-5 py-2">Status</th>
              <th className="px-5 py-2">Accuracy</th>
              <th className="px-5 py-2 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--border)] text-[12px]">
            {versions.map((v, index) => {
              const isArchived = v.status === 'archived';
              return (
                <tr key={index} className="hover:bg-[var(--bg-base)] transition-colors">
                  <td className="px-5 py-2.5 font-medium text-[var(--text-primary)]">
                    {v.version !== null && v.version !== undefined ? `v${v.version}` : 'N/A'}
                  </td>
                  <td className="px-5 py-2.5">
                    <span className="text-[11px] text-[var(--text-secondary)]">
                      {formatStatus(v.status)}
                    </span>
                  </td>
                  <td className="px-5 py-2.5 text-[var(--text-primary)] font-mono text-[11px]">
                    {v.accuracy !== null && v.accuracy !== undefined ? formatPercent(v.accuracy) : 'N/A'}
                  </td>
                  <td className="px-5 py-2.5 text-right">
                    {isArchived ? (
                      <button
                        onClick={() => onRollback(v.version)}
                        className="inline-flex items-center space-x-1.5 text-[12px] font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
                      >
                        <RefreshCw className="w-3 h-3" />
                        <span>Rollback</span>
                      </button>
                    ) : (
                      <span className="text-[12px] text-[var(--text-muted)]">Active</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
