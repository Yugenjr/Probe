import { Search, Command as CommandIcon, Bell, ChevronRight } from "lucide-react";
import { useRouterState } from "@tanstack/react-router";
import { Link } from "@tanstack/react-router";

function labelFor(segment: string) {
  return segment.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function TopBar() {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const parts = pathname.split("/").filter(Boolean);

  return (
    <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-border bg-background/80 px-4 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <nav className="flex items-center gap-1.5 text-[13px] text-muted-foreground">
        <Link to="/" className="hover:text-foreground">
          probe
        </Link>
        {parts.map((p, i) => {
          const to = "/" + parts.slice(0, i + 1).join("/");
          const last = i === parts.length - 1;
          return (
            <span key={to} className="flex items-center gap-1.5">
              <ChevronRight className="size-3.5 text-border-strong" />
              {last ? (
                <span className="text-foreground font-medium">{labelFor(p)}</span>
              ) : (
                <Link to={to} className="hover:text-foreground">
                  {labelFor(p)}
                </Link>
              )}
            </span>
          );
        })}
        {parts.length === 0 && (
          <>
            <ChevronRight className="size-3.5 text-border-strong" />
            <span className="text-foreground font-medium">Dashboard</span>
          </>
        )}
      </nav>

      <div className="ml-auto flex items-center gap-2">
        <button className="group inline-flex h-8 items-center gap-2 rounded-md border border-border bg-surface px-2.5 text-[12px] text-muted-foreground transition-colors hover:border-border-strong hover:text-foreground">
          <Search className="size-3.5" />
          <span className="hidden sm:inline">Search investigations…</span>
          <span className="ml-2 hidden items-center gap-1 rounded border border-border bg-background px-1.5 py-0.5 text-[10px] text-muted-foreground sm:flex">
            <CommandIcon className="size-2.5" />K
          </span>
        </button>
        <button
          className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-border bg-surface text-muted-foreground transition-colors hover:border-border-strong hover:text-foreground"
          aria-label="Notifications"
        >
          <Bell className="size-3.5" />
        </button>
        <div className="ml-1 flex size-8 items-center justify-center rounded-full bg-primary/15 text-[11px] font-semibold text-primary ring-1 ring-inset ring-primary/25">
          KM
        </div>
      </div>
    </header>
  );
}
