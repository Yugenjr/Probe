import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { RefreshCw, Bell } from 'lucide-react';
import { getMe } from '../lib/api';

const PAGE_TITLES = {
  '/dashboard': { label: 'Fleet Overview' },
  '/docs':      { label: 'Documentation' },
  '/settings':  { label: 'Settings' },
};

export default function TopBar({ onRefresh, lastUpdated, isRefreshing }) {
  const router = useRouter();
  const [user, setUser] = useState(null);

  useEffect(() => {
    async function loadUser() {
      try {
        const data = await getMe();
        setUser(data);
      } catch (err) { /* silent */ }
    }
    loadUser();
  }, []);

  const page = PAGE_TITLES[router.pathname] ||
    (router.pathname.startsWith('/models/') ? { label: `Model / ${router.query.id || ''}` } : { label: 'Overview' });

  return (
    <header className="h-[64px] flex items-center justify-between px-6 bg-[var(--bg-surface)] border-b border-[var(--border)] sticky top-0 z-40 shrink-0">
      {/* Left: breadcrumb + title */}
      <div className="flex items-center gap-2">
        <div className="flex items-center gap-2 text-sm">
          <span className="text-[var(--text-secondary)]">DriftGuard</span>
          <span className="text-[var(--border-hover)]">/</span>
          <span className="font-medium text-[var(--text-primary)]">{page.label}</span>
        </div>
      </div>

      {/* Right: sync + user */}
      <div className="flex items-center gap-4">
        {onRefresh && (
          <div className="flex items-center gap-3">
            <button
              onClick={onRefresh}
              disabled={isRefreshing}
              title="Refresh data"
              className="p-1.5 text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors rounded-md hover:bg-[var(--bg-base)] disabled:opacity-50"
            >
              <RefreshCw size={16} className={`${isRefreshing ? 'animate-spin' : ''}`} />
            </button>
          </div>
        )}

        <div className="w-[1px] h-5 bg-[var(--border)]" />

        <button className="p-1.5 text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors rounded-md hover:bg-[var(--bg-base)]">
          <Bell size={16} />
        </button>

        <div className="w-[1px] h-5 bg-[var(--border)]" />

        <div className="flex items-center gap-2 cursor-pointer group">
          <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-[#000000] to-[#666666] flex items-center justify-center text-[10px] font-medium text-white shadow-sm ring-1 ring-black/10">
            {user ? user.name?.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) : 'DG'}
          </div>
        </div>
      </div>
    </header>
  );
}
