import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { LayoutDashboard, Activity, Settings, LogOut, BookOpen, Github } from 'lucide-react';
import { getMe } from '../lib/api';

export default function Sidebar({ activeModelCount }) {
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

  const handleSignOut = () => {
    localStorage.removeItem('dg_api_key');
    router.replace('/login');
  };

  const navItems = [
    { label: 'Overview',  icon: LayoutDashboard, path: '/dashboard', match: (p) => p === '/dashboard' },
    { label: 'Models',    icon: Activity,        path: '#',           match: (p) => p.startsWith('/models/'), badge: activeModelCount },
    { label: 'Docs',      icon: BookOpen,        path: '/docs',       match: (p) => p.startsWith('/docs') },
    { label: 'Settings',  icon: Settings,        path: '/settings',   match: (p) => p.startsWith('/settings') },
  ];

  return (
    <aside className="w-[240px] min-w-[240px] bg-[var(--bg-surface)] border-r border-[var(--border)] flex flex-col h-screen sticky top-0 z-50">
      {/* Brand */}
      <div className="h-[64px] flex items-center px-6 border-b border-[var(--border)]">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 bg-black rounded-md flex items-center justify-center">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
            </svg>
          </div>
          <span className="font-semibold text-[15px] tracking-tight text-[var(--text-primary)]">DriftGuard</span>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-4 py-6 flex flex-col gap-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = item.match(router.pathname);
          return (
            <button
              key={item.label}
              onClick={() => item.path !== '#' && router.push(item.path)}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-md text-[14px] transition-colors ${
                active 
                  ? 'bg-[var(--bg-base)] text-[var(--text-primary)] font-medium'
                  : 'text-[var(--text-secondary)] hover:bg-[var(--bg-base)] hover:text-[var(--text-primary)]'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon size={16} />
                <span>{item.label}</span>
              </div>
              {item.badge > 0 && (
                <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-[var(--bg-base)] border border-[var(--border)] text-[var(--text-secondary)]">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer links */}
      <div className="px-4 py-4 border-t border-[var(--border)]">
        <a
          href="https://github.com/Yugenjr/Probe"
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-3 px-3 py-2 rounded-md text-[14px] text-[var(--text-secondary)] hover:bg-[var(--bg-base)] hover:text-[var(--text-primary)] transition-colors"
        >
          <Github size={16} />
          <span>GitHub</span>
        </a>
      </div>

      {/* User profile */}
      <div className="p-4 border-t border-[var(--border)]">
        <div className="flex items-center gap-3 px-3 py-2 mb-2">
          <div className="w-8 h-8 rounded-full bg-[var(--bg-base)] border border-[var(--border)] flex items-center justify-center text-[11px] font-medium text-[var(--text-primary)]">
            {user ? user.name?.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) : 'DG'}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-[13px] font-medium text-[var(--text-primary)] truncate">
              {user ? user.name : 'DriftGuard User'}
            </div>
          </div>
        </div>
        <button
          onClick={handleSignOut}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-md text-[14px] text-[var(--text-secondary)] hover:bg-[var(--bg-base)] hover:text-[var(--text-primary)] transition-colors"
        >
          <LogOut size={16} />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
}
