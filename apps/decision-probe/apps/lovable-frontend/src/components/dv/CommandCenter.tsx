import { session } from "./data";
import { Kbd, TaskGlyph } from "./atoms";

const slashCommands = ["/investigate", "/explain", "/diff", "/rollback", "/summarise"];

export function CommandCenter() {
  return (
    <aside className="flex h-full min-h-0 w-full flex-col bg-panel">
      {/* header */}
      <div className="flex h-11 shrink-0 items-center justify-between border-b border-border-subtle px-3">
        <div className="flex items-center gap-2">
          <span className="text-[13px] font-medium text-fg-strong">Command Center</span>
          <span className="mono text-[10.5px] text-fg-muted">· INC-2043</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1 text-[11px] text-fg-muted">
            <span className="mono text-info">⟳</span> 1 running
          </span>
          <Kbd>⌘J</Kbd>
        </div>
      </div>

      {/* stream */}
      <div className="flex-1 min-h-0 overflow-y-auto px-3 py-3">
        {session.map((turn, i) => (
          <div key={i} className="fade-in mb-4">
            <div className="mb-1 flex items-center gap-2 text-[11px]">
              <span className="mono text-fg-muted">{turn.time}</span>
              <span className={turn.who === "you" ? "text-fg-strong" : "text-accent"}>
                {turn.who === "you" ? "You" : "DecisionVerse"}
              </span>
            </div>
            <div className="pl-8 text-[12.5px] text-foreground">
              {turn.text}
              {i === session.length - 1 && <span className="caret ml-0.5" />}
            </div>
            {"tasks" in turn && turn.tasks && turn.tasks.length > 0 && (
              <ul className="mt-1 space-y-0.5 pl-8">
                {turn.tasks.map((t, j) => (
                  <li key={j} className="flex items-center gap-2 text-[11.5px]">
                    <TaskGlyph state={t.state} />
                    <span className="min-w-0 flex-1 truncate text-fg-muted">{t.label}</span>
                    {t.dur && <span className="mono text-[10.5px] text-fg-muted">{t.dur}</span>}
                  </li>
                ))}
                {turn.tasks.some((t) => t.state === "running") && (
                  <li className="ml-4 mt-1 h-px w-24 indeterminate">
                    <span className="indeterminate-bar" />
                  </li>
                )}
              </ul>
            )}
          </div>
        ))}
      </div>

      {/* slash */}
      <div className="shrink-0 border-t border-border-subtle px-3 pt-2">
        <div className="flex flex-wrap gap-1 pb-2">
          {slashCommands.map((c) => (
            <button key={c} className="mono rounded border border-border-subtle bg-raised/40 px-1.5 py-0.5 text-[11px] text-fg-muted hover:border-border hover:text-foreground">
              {c}
            </button>
          ))}
        </div>
      </div>

      {/* composer */}
      <div className="shrink-0 px-3 pb-3">
        <div className="rounded-md border border-border bg-raised">
          <textarea
            rows={3}
            placeholder="Investigate this incident…"
            className="block w-full resize-none bg-transparent px-2.5 py-2 text-[12.5px] text-foreground placeholder:text-fg-muted focus:outline-none"
          />
          <div className="flex items-center justify-between border-t border-border-subtle px-2 py-1.5">
            <div className="flex items-center gap-2 text-[11px] text-fg-muted">
              <button className="mono hover:text-foreground">@evidence</button>
              <button className="mono hover:text-foreground">@timeline</button>
              <button className="mono hover:text-foreground">#INC-2011</button>
            </div>
            <div className="flex items-center gap-1.5 text-[11px] text-fg-muted">
              run <Kbd>⌘↵</Kbd>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
