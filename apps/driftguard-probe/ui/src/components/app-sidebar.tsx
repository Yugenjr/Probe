import { Link, useRouterState } from "@tanstack/react-router";
import {
  LayoutDashboard,
  Search,
  FileText,
  BookOpen,
  Settings,
  Github,
  BookMarked,
  Radar,
} from "lucide-react";
import { cn } from "@/lib/utils";

type NavItem = {
  to: "/" | "/investigations" | "/reports" | "/knowledge-base" | "/settings";
  label: string;
  icon: typeof LayoutDashboard;
  exact?: boolean;
};

const nav: NavItem[] = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, exact: true },
  { to: "/investigations", label: "Investigations", icon: Search },
  { to: "/reports", label: "Reports", icon: FileText },
  { to: "/knowledge-base", label: "Knowledge Base", icon: BookOpen },
  { to: "/settings", label: "Settings", icon: Settings },
];

export function AppSidebar() {
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  return (
    <aside className="hidden md:flex w-60 shrink-0 flex-col border-r border-border bg-sidebar text-sidebar-foreground">
      <div className="flex h-14 items-center gap-2 px-4 border-b border-sidebar-border">
        <div className="flex size-7 items-center justify-center rounded-md bg-primary/15 text-primary ring-1 ring-inset ring-primary/25">
          <Radar className="size-4" />
        </div>
        <div className="flex flex-col leading-tight">
          <span className="text-[13px] font-semibold text-foreground tracking-tight">
            DriftGuard
          </span>
          <span className="text-[10px] font-medium uppercase tracking-[0.12em] text-muted-foreground">
            Probe
          </span>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto p-2">
        <div className="px-2 pb-1.5 pt-2 text-[10px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
          Workspace
        </div>
        <ul className="space-y-0.5">
          {nav.map((item) => {
            const active = item.exact
              ? pathname === item.to
              : pathname === item.to || pathname.startsWith(item.to + "/");
            const Icon = item.icon;
            return (
              <li key={item.to}>
                <Link
                  to={item.to}
                  className={cn(
                    "group flex items-center gap-2.5 rounded-md px-2.5 py-1.5 text-[13px] font-medium transition-colors",
                    active
                      ? "bg-sidebar-accent text-foreground"
                      : "text-sidebar-foreground hover:bg-sidebar-accent/60 hover:text-foreground",
                  )}
                >
                  <Icon
                    className={cn(
                      "size-4 shrink-0",
                      active ? "text-primary" : "text-muted-foreground group-hover:text-foreground",
                    )}
                  />
                  <span>{item.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>

        <div className="mt-6 rounded-md border border-sidebar-border bg-sidebar-accent/40 p-3">
          <div className="flex items-center gap-2 text-[11px] font-medium text-foreground">
            <span className="size-1.5 rounded-full bg-success animate-pulse" />
            Probe engine online
          </div>
          <p className="mt-1 text-[11px] leading-relaxed text-muted-foreground">
            2 investigations in flight · avg. runtime 5m 42s
          </p>
        </div>
      </nav>

      <div className="border-t border-sidebar-border p-2">
        <a
          href="https://github.com"
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-2.5 rounded-md px-2.5 py-1.5 text-[12px] text-sidebar-foreground hover:bg-sidebar-accent/60 hover:text-foreground"
        >
          <Github className="size-4 text-muted-foreground" />
          GitHub
        </a>
        <a
          href="#"
          className="flex items-center gap-2.5 rounded-md px-2.5 py-1.5 text-[12px] text-sidebar-foreground hover:bg-sidebar-accent/60 hover:text-foreground"
        >
          <BookMarked className="size-4 text-muted-foreground" />
          Documentation
        </a>
        <div className="mt-1 px-2.5 py-1 text-[10px] text-muted-foreground">
          v0.4.2 · commit 2f7a91c
        </div>
      </div>
    </aside>
  );
}
