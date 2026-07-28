import React from "react";
import { NavLink, Outlet } from "react-router-dom";
import {
  Inbox,
  History,
  BookOpen,
  Layers,
  Settings,
  Terminal,
  Shield,
  Search,
  User,
} from "lucide-react";

export const WorkspaceLayout = () => {
  const navItems = [
    { label: "Investigations", path: "/investigations", icon: Inbox, badge: "3 Active" },
    { label: "History", path: "/history", icon: History },
    { label: "Knowledge", path: "/knowledge", icon: BookOpen },
    { label: "Platforms", path: "/platforms", icon: Layers, badge: "5 Linked" },
    { label: "Settings", path: "/settings", icon: Settings },
  ];

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background text-foreground font-sans antialiased select-none">
      {/* Fixed Desktop Navigation Sidebar */}
      <aside className="w-56 border-r border-border bg-card flex flex-col justify-between shrink-0">
        <div className="p-4">
          <div className="flex items-center space-x-2.5 pb-4 border-b border-border">
            <div className="p-1.5 bg-blue-600/20 border border-blue-500/40 rounded flex items-center justify-center text-blue-400 shrink-0">
              <Terminal className="w-4 h-4" />
            </div>
            <div>
              <h1 className="text-sm font-bold tracking-tight text-slate-100">Probe Engine</h1>
              <p className="text-[11px] text-slate-400 font-mono">AI Investigation Suite</p>
            </div>
          </div>

          <nav className="mt-4 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center justify-between px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                      isActive
                        ? "bg-slate-800 text-white font-semibold shadow-sm"
                        : "text-slate-400 hover:bg-slate-900/80 hover:text-slate-200"
                    }`
                  }
                >
                  <div className="flex items-center space-x-2.5">
                    <Icon className="w-4 h-4 text-slate-400 shrink-0" />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className="text-[10px] px-1.5 py-0.5 bg-slate-900 border border-slate-700 text-slate-300 rounded font-mono">
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              );
            })}
          </nav>
        </div>

        <div className="p-4 border-t border-border bg-slate-950/60 space-y-2.5">
          <div className="flex items-center justify-between text-[11px] font-mono text-slate-400">
            <span className="flex items-center gap-1.5 text-emerald-400">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              Tenant: Prod-East
            </span>
            <span>v2.0</span>
          </div>
          <div className="flex items-center space-x-2 pt-2 border-t border-slate-900 text-xs text-slate-300">
            <User className="w-3.5 h-3.5 text-slate-400 shrink-0" />
            <span className="truncate font-mono text-[11px]">sre-lead@driftguard.ai</span>
          </div>
        </div>
      </aside>

      {/* Main Workspace Frame */}
      <div className="flex-1 flex flex-col h-full min-w-0 overflow-hidden">
        <header className="h-12 border-b border-border bg-card/70 flex items-center justify-between px-6 shrink-0 z-10">
          <div className="flex items-center space-x-3 w-96">
            <div className="relative w-full">
              <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Search investigation sessions or runbooks (⌘K)"
                className="w-full bg-slate-900 border border-slate-800 rounded text-xs pl-8 pr-3 py-1 text-slate-200 focus:outline-none focus:border-slate-600 font-mono placeholder:font-sans placeholder:text-slate-500"
              />
            </div>
          </div>
          <div className="flex items-center space-x-2 text-xs text-slate-400 font-mono">
            <Shield className="w-3.5 h-3.5 text-emerald-400" />
            <span>Sandboxed Execution: Zero Ambient Key Access</span>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto bg-background">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
