import React, { useState, useEffect } from 'react';
import { Search, Command, FileText, Server, AlertCircle } from 'lucide-react';

export function SearchDialog({ isOpen, onClose }: { isOpen: boolean, onClose: () => void }) {
  const [query, setQuery] = useState('');

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        isOpen ? onClose() : document.dispatchEvent(new CustomEvent('openSearch')); // Simplified toggle
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh] sm:pt-[20vh]">
      <div className="fixed inset-0 bg-background/80 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-lg overflow-hidden rounded-xl border border-border bg-panel shadow-2xl animate-in fade-in zoom-in-95">
        <div className="flex items-center border-b border-border-subtle px-4">
          <Search size={18} className="text-fg-muted mr-3" />
          <input
            autoFocus
            value={query}
            onChange={e => setQuery(e.target.value)}
            className="flex h-14 w-full bg-transparent text-[14px] outline-none placeholder:text-fg-muted text-foreground"
            placeholder="Search investigations, insights, or commands..."
          />
          <div className="flex items-center gap-1">
            <kbd className="kbd">ESC</kbd>
          </div>
        </div>
        <div className="max-h-[300px] overflow-y-auto p-2">
          {query.length === 0 ? (
            <div className="p-4 text-center text-[12px] text-fg-muted">
              Start typing to search across DecisionVerse...
            </div>
          ) : (
            <div className="space-y-1">
              <div className="px-3 py-1.5 text-[10px] font-bold tracking-widest text-fg-muted uppercase">Investigations</div>
              <button className="w-full flex items-center gap-3 rounded-md px-3 py-2 text-left text-[13px] hover:bg-raised text-foreground group">
                <AlertCircle size={15} className="text-danger" />
                <span className="flex-1">Database connection timeout in us-east-1</span>
                <span className="text-[10px] text-fg-muted opacity-0 group-hover:opacity-100 transition-opacity">Jump to</span>
              </button>
              
              <div className="px-3 py-1.5 text-[10px] font-bold tracking-widest text-fg-muted uppercase mt-3">Evidence</div>
              <button className="w-full flex items-center gap-3 rounded-md px-3 py-2 text-left text-[13px] hover:bg-raised text-foreground group">
                <Server size={15} className="text-info" />
                <span className="flex-1">kubectl logs prod-db-primary</span>
              </button>
              <button className="w-full flex items-center gap-3 rounded-md px-3 py-2 text-left text-[13px] hover:bg-raised text-foreground group">
                <FileText size={15} className="text-warning" />
                <span className="flex-1">incident-report-1029.pdf</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
