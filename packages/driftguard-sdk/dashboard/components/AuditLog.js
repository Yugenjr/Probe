import React, { useState } from 'react';
import { Activity, Search, Filter, ChevronLeft, ChevronRight } from 'lucide-react';
import { formatDate } from '../lib/utils';

export default function AuditLog({ logs }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 8;

  if (!logs || logs.length === 0) {
    return (
      <div className="bg-[var(--bg-surface)] border border-[var(--border)] p-4 rounded-lg text-center text-[var(--text-muted)] text-[13px]">
        No audit logs available for this model.
      </div>
    );
  }

  const getEventStyle = (type) => {
    switch (type) {
      case 'model_registered':
        return 'text-[var(--amber)] bg-[var(--amber-dim)] border border-[var(--amber)]/20';
      case 'drift_detected':
        return 'text-[var(--red)] bg-[var(--red-dim)] border border-[var(--red)]/20';
      case 'retraining_triggered':
        return 'text-[var(--blue)] bg-[var(--blue-dim)] border border-[var(--blue)]/20';
      case 'retraining_completed':
        return 'text-[var(--green)] bg-[var(--green-dim)] border border-[var(--green)]/20';
      case 'retraining_failed':
        return 'text-[var(--red)] bg-[var(--red-dim)] border border-[var(--red)]/20';
      default:
        return 'text-[var(--text-primary)] bg-[var(--bg-base)] border border-[var(--border)]';
    }
  };

  const formatEventName = (type) => {
    return type.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  };

  const filteredLogs = logs.filter(log => {
    const matchesSearch = 
      log.event_type.toLowerCase().includes(searchTerm.toLowerCase()) || 
      (log.details && JSON.stringify(log.details).toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesFilter = filterType === 'all' || log.event_type.includes(filterType);
    return matchesSearch && matchesFilter;
  });

  const totalPages = Math.ceil(filteredLogs.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const currentLogs = filteredLogs.slice(startIndex, startIndex + pageSize);

  return (
    <div className="bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg flex flex-col h-[500px]">
      <div className="p-4 border-b border-[var(--border)]">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-[13px] font-semibold text-[var(--text-primary)] flex items-center">
            <Activity className="w-4 h-4 mr-2 text-[var(--text-secondary)]" />
            Audit Trail
          </h3>
          <span className="px-2 py-0.5 text-[11px] font-medium bg-[var(--bg-base)] text-[var(--text-secondary)] border border-[var(--border)] rounded">
            {logs.length} Total Events
          </span>
        </div>

        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-2.5 top-2 w-3.5 h-3.5 text-[var(--text-muted)]" />
            <input
              type="text"
              placeholder="Search logs..."
              value={searchTerm}
              onChange={(e) => { setSearchTerm(e.target.value); setCurrentPage(1); }}
              className="w-full bg-[var(--bg-base)] border border-[var(--border)] text-[var(--text-primary)] text-[12px] rounded-md pl-8 pr-3 py-1.5 focus:outline-none focus:border-[var(--border-hover)] transition-colors"
            />
          </div>
          <div className="relative">
            <Filter className="absolute left-2.5 top-2 w-3.5 h-3.5 text-[var(--text-muted)]" />
            <select
              value={filterType}
              onChange={(e) => { setFilterType(e.target.value); setCurrentPage(1); }}
              className="appearance-none bg-[var(--bg-base)] border border-[var(--border)] text-[var(--text-primary)] text-[12px] rounded-md pl-8 pr-8 py-1.5 focus:outline-none focus:border-[var(--border-hover)] transition-colors cursor-pointer"
            >
              <option value="all">All Events</option>
              <option value="drift">Drift Events</option>
              <option value="retrain">Retraining</option>
              <option value="register">Registration</option>
            </select>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-auto">
        <table className="w-full text-left border-collapse">
          <thead className="sticky top-0 bg-[var(--bg-base)] z-10 border-b border-[var(--border)]">
            <tr>
              <th className="px-3 py-1.5 text-[var(--text-secondary)] font-semibold text-[11px]">Timestamp</th>
              <th className="px-3 py-1.5 text-[var(--text-secondary)] font-semibold text-[11px]">Event Type</th>
              <th className="px-3 py-1.5 text-[var(--text-secondary)] font-semibold text-[11px]">Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--border)]">
            {currentLogs.length === 0 ? (
              <tr>
                <td colSpan={3} className="px-3 py-6 text-center text-[var(--text-muted)] text-[12px]">
                  No events found matching your filters.
                </td>
              </tr>
            ) : (
              currentLogs.map((log, index) => (
                <tr key={index} className="hover:bg-[var(--bg-base)] transition-colors">
                  <td className="px-3 py-2 text-[11px] text-[var(--text-secondary)] whitespace-nowrap align-top font-mono">
                    {formatDate(log.timestamp)}
                  </td>
                  <td className="px-3 py-2 align-top">
                    <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium ${getEventStyle(log.event_type)}`}>
                      {formatEventName(log.event_type)}
                    </span>
                  </td>
                  <td className="px-3 py-2 text-[12px] text-[var(--text-primary)] align-top">
                    <div className="font-mono text-[10px] text-[var(--text-secondary)] overflow-x-auto whitespace-pre">
                      {log.details ? JSON.stringify(log.details, null, 2) : '-'}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="p-3 border-t border-[var(--border)] flex items-center justify-between">
          <span className="text-[11px] text-[var(--text-secondary)]">
            Showing <span className="font-medium text-[var(--text-primary)]">{logs.length === 0 ? 0 : startIndex + 1}</span> to <span className="font-medium text-[var(--text-primary)]">{Math.min(startIndex + pageSize, filteredLogs.length)}</span> of <span className="font-medium text-[var(--text-primary)]">{filteredLogs.length}</span>
          </span>
          <div className="flex gap-1">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1 || logs.length === 0}
              className="p-1 rounded border border-[var(--border)] hover:bg-[var(--bg-base)] text-[var(--text-primary)] disabled:opacity-50 transition-colors"
            >
              <ChevronLeft size={14} />
            </button>
            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages || logs.length === 0}
              className="p-1 rounded border border-[var(--border)] hover:bg-[var(--bg-base)] text-[var(--text-primary)] disabled:opacity-50 transition-colors"
            >
              <ChevronRight size={14} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
