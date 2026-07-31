import React, { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import TopBar from './TopBar';
import { getModels } from '../lib/api';
import { ShieldAlert } from 'lucide-react';

export default function Layout({ children, onRefresh, lastUpdated, isRefreshing, error }) {
  const [activeCount, setActiveCount] = useState(0);

  useEffect(() => {
    async function loadActiveCount() {
      try {
        const data = await getModels();
        if (Array.isArray(data)) setActiveCount(data.length);
      } catch (err) { /* silent */ }
    }
    loadActiveCount();
  }, [children]);

  return (
    <div className="flex bg-[var(--bg-base)] min-h-screen text-[var(--text-primary)] font-sans antialiased">
      <Sidebar activeModelCount={activeCount} />

      <div className="flex-1 flex flex-col h-screen overflow-y-auto">
        <TopBar onRefresh={onRefresh} lastUpdated={lastUpdated} isRefreshing={isRefreshing} />

        <main className="flex-1 p-6 w-full mx-auto">
          {error && (
            <div className="flex items-start gap-3 p-4 mb-6 rounded-md bg-[var(--red-dim)] border border-[var(--red)] text-[var(--red)]">
              <ShieldAlert size={16} className="shrink-0 mt-0.5" />
              <div>
                <div className="text-sm font-semibold mb-1">Connection Error</div>
                <div className="text-xs text-[var(--red)]">{error}</div>
              </div>
            </div>
          )}
          {children}
        </main>
      </div>
    </div>
  );
}
