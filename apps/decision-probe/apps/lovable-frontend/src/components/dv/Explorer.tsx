import { investigations } from "./data";
import { SeverityDot, StatusGlyph, Kbd } from "./atoms";

const groups = [
  { label: "Pinned", filter: (i: typeof investigations[number]) => i.pinned },
  { label: "Active", filter: (i: typeof investigations[number]) => !i.pinned && i.status === "active" },
  { label: "Recent", filter: (i: typeof investigations[number]) => !i.pinned && i.status !== "active" },
];

export function Explorer({ selectedId, onSelect }: { selectedId: string; onSelect: (id: string) => void }) {
  return (
    <aside className="flex h-full min-h-0 w-full flex-col bg-panel">
      {/* brand */}
      <div className="flex h-11 shrink-0 items-center justify-between px-3">
        <div className="flex items-center gap-2">
          <div className="grid h-4 w-4 place-items-center">
            <span className="block h-2 w-2 rotate-45 bg-fg-strong" />
          </div>
          <span className="text-[13px] font-medium tracking-tight text-fg-strong">DecisionVerse</span>
        </div>
        <Kbd>⌘K</Kbd>
      </div>

      {/* search */}
      <div className="px-3 pb-2">
        <div className="group flex h-7 items-center gap-2 rounded-md border border-transparent bg-raised px-2 hover:border-border-subtle">
          <span className="mono text-[10px] text-fg-muted">⌕</span>
          <input
            placeholder="Search investigations…"
            className="min-w-0 flex-1 bg-transparent text-[12px] text-foreground placeholder:text-fg-muted focus:outline-none"
          />
          <Kbd>⌘P</Kbd>
        </div>
      </div>

      {/* new investigation */}
      <button className="mx-3 mb-2 flex h-7 items-center justify-between rounded-md border border-border-subtle px-2 text-[12px] text-foreground transition-colors hover:bg-raised">
        <span className="flex items-center gap-2">
          <span className="mono text-fg-muted">+</span>
          New Investigation
        </span>
        <Kbd>⌘N</Kbd>
      </button>

      {/* lists */}
      <div className="flex-1 min-h-0 overflow-y-auto px-1 pb-2">
        {groups.map((g) => {
          const items = investigations.filter(g.filter);
          if (!items.length) return null;
          return (
            <div key={g.label} className="mt-3">
              <div className="px-3 pb-1 text-micro">{g.label}</div>
              <ul>
                {items.map((i) => {
                  const active = i.id === selectedId;
                  return (
                    <li key={i.id}>
                      <button
                        onClick={() => onSelect(i.id)}
                        className={`group relative flex h-[26px] w-full items-center gap-2 pr-2 pl-3 text-left text-[12.5px] transition-colors ${
                          active ? "bg-raised text-fg-strong" : "text-foreground hover:bg-raised/60"
                        }`}
                      >
                        {active && <span className="absolute left-0 top-1 bottom-1 w-[2px] rounded-r bg-accent" />}
                        <StatusGlyph status={i.status} />
                        <SeverityDot severity={i.severity} />
                        <span className="mono shrink-0 text-[11px] text-fg-muted">{i.id}</span>
                        <span className="min-w-0 flex-1 truncate">{i.title}</span>
                        <span className="mono shrink-0 text-[10.5px] text-fg-muted">{i.updated}</span>
                      </button>
                    </li>
                  );
                })}
              </ul>
            </div>
          );
        })}
      </div>

      {/* footer */}
      <div className="shrink-0 border-t border-border-subtle px-3 py-2">
        <div className="flex items-center justify-between text-[11.5px] text-fg-muted">
          <span className="flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-success" />
            Payments Platform
          </span>
          <span className="flex items-center gap-1">
            Settings <Kbd>⌘,</Kbd>
          </span>
        </div>
      </div>
    </aside>
  );
}
