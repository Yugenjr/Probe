import React from 'react';

export default function ConfirmModal({ isOpen, title, message, onConfirm, onCancel, confirmColor }) {
  if (!isOpen) return null;

  const confirmBtnClass = confirmColor === 'red'
    ? 'bg-[#f85149] hover:bg-[#f85149]/80 text-[#ededed] border-[#f85149]'
    : 'bg-[#24b47e] hover:bg-[#24b47e]/80 text-[#0d1117] border-[#24b47e]';

  return (
    <div 
      className="absolute top-0 left-0 w-full min-h-screen bg-black/60 flex items-center justify-center p-4 z-50"
      style={{ backdropFilter: 'blur(4px)' }}
    >
      <div className="bg-[var(--bg-surface)] border border-[var(--border)] rounded-xl max-w-md w-full p-6 shadow-xl shadow-black/10 animate-pulse-slow">
        <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">{title}</h3>
        <p className="text-sm text-[var(--text-secondary)] mb-6 leading-relaxed">{message}</p>
        <div className="flex justify-end space-x-3">
          <button
            onClick={onCancel}
            type="button"
            className="px-4 py-2 text-sm font-semibold rounded-xl bg-[var(--bg-raised)] border border-[var(--border)] hover:bg-[var(--bg-overlay)] text-[var(--text-primary)] transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            type="button"
            className={`px-4 py-2 text-sm font-semibold rounded-xl border transition-colors ${confirmBtnClass}`}
          >
            Confirm
          </button>
        </div>
      </div>
    </div>
  );
}
