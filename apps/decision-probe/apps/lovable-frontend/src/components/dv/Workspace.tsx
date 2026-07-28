import { useState, type ReactNode } from "react";
import { evidence, timeline, metrics, reasoning, hypotheses, actions } from "./data";
import { Confidence, Kbd, SeverityDot, SourceTag, Sparkline } from "./atoms";

function Section({
  n, title, count, defaultOpen = true, action, children,
}: {
  n: number; title: string; count?: number | string; defaultOpen?: boolean; action?: ReactNode; children: ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <section className="border-t border-border-subtle">
      <header className="sticky top-0 z-10 flex h-8 items-center bg-background/90 backdrop-blur-sm">
        <button
          onClick={() => setOpen((v) => !v)}
          className="group flex flex-1 items-center gap-2 pl-4 pr-2 text-left"
        >
          <span className="mono w-3 text-[10px] text-fg-muted transition-transform" style={{ transform: open ? "rotate(90deg)" : "none" }}>›</span>
          <span className="text-micro">{title}</span>
          {count !== undefined && <span className="mono text-[10.5px] text-fg-muted">· {count}</span>}
          <span className="ml-auto mono text-[10px] text-fg-muted opacity-0 transition-opacity group-hover:opacity-100">⌘⌥{n}</span>
        </button>
        {action && open && <div className="pr-4">{action}</div>}
      </header>
      {open && <div className="fade-in pb-4">{children}</div>}
    </section>
  );
}

function Row({ children, onClick }: { children: ReactNode; onClick?: () => void }) {
  return (
    <div
      onClick={onClick}
      className="group flex h-7 cursor-default items-center gap-3 px-4 text-[12.5px] transition-colors hover:bg-raised/50"
    >
      {children}
    </div>
  );
}

export function Workspace() {
  return (
    <div className="flex h-full min-h-0 flex-col bg-background">
      {/* breadcrumb */}
      <div className="flex h-7 shrink-0 items-center justify-between border-b border-border-subtle px-4 text-[11.5px] text-fg-muted">
        <div className="flex items-center gap-1.5 min-w-0">
          <span className="truncate">Payments Platform</span>
          <span className="text-fg-muted/60">/</span>
          <span className="truncate">Investigations</span>
          <span className="text-fg-muted/60">/</span>
          <span className="mono text-foreground truncate">INC-2043</span>
        </div>
        <Kbd>⌘K</Kbd>
      </div>

      {/* scroll region */}
      <div className="flex-1 min-h-0 overflow-y-auto">
        {/* header */}
        <div className="px-4 pt-4 pb-3">
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <span className="mono text-[11px] text-fg-muted">INC-2043</span>
                <h1 className="truncate text-[15px] font-medium text-fg-strong">Payments Gateway Outage</h1>
              </div>
              <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-[11.5px] text-fg-muted">
                <span className="flex items-center gap-1.5"><SeverityDot severity="critical" /> Critical</span>
                <span className="flex items-center gap-1.5">
                  <span className="relative flex h-1.5 w-1.5">
                    <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-info opacity-50" />
                    <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-info" />
                  </span>
                  Investigating
                </span>
                <span>Started <span className="mono text-foreground">14:42 UTC</span></span>
                <span>Updated <span className="mono text-foreground">30s</span> ago</span>
                <span>Owner <span className="text-foreground">@maya</span></span>
                <span>Region <span className="mono text-foreground">us-east-1</span></span>
                <span>Services <span className="mono text-foreground">payments-api, ledger</span></span>
              </div>
            </div>
            <div className="flex shrink-0 items-center gap-1">
              {["Share", "Export", "Upload"].map((l, i) => (
                <button key={l} className="flex h-6 items-center gap-1 rounded border border-border-subtle bg-raised/40 px-2 text-[11.5px] text-foreground hover:bg-raised">
                  {l}
                  {i === 2 && <Kbd>⌘⇧U</Kbd>}
                </button>
              ))}
              <button className="grid h-6 w-6 place-items-center rounded border border-border-subtle bg-raised/40 text-fg-muted hover:bg-raised">⋯</button>
            </div>
          </div>
        </div>

        {/* Incident */}
        <Section n={1} title="Incident">
          <dl className="grid grid-cols-[120px_1fr] gap-x-4 gap-y-1 px-4 text-[12.5px]">
            {[
              ["Title", "Payments Gateway Outage"],
              ["Description", "Elevated 5xx from payments-api after 14:41 UTC. Customer checkouts failing intermittently."],
              ["Severity", "Critical"],
              ["Status", "Investigating"],
              ["Affected", "payments-api, ledger, checkout-web"],
              ["Region", "us-east-1"],
              ["Started", "2026-07-27 14:42:11 UTC"],
              ["Reporter", "@alerts-bot (PagerDuty)"],
            ].map(([k, v]) => (
              <div key={k} className="contents">
                <dt className="text-fg-muted">{k}</dt>
                <dd className="text-foreground">{v}</dd>
              </div>
            ))}
          </dl>
        </Section>

        {/* Evidence */}
        <Section n={2} title="Evidence" count={evidence.length} action={
          <button className="flex h-5 items-center gap-1 text-[11.5px] text-fg-muted hover:text-foreground">
            <span className="mono">+</span> Add
          </button>
        }>
          {evidence.map((e, i) => (
            <Row key={i}>
              <span className="mono w-3 text-[10px] text-fg-muted">›</span>
              <SourceTag source={e.source} />
              <span className="min-w-0 flex-1 truncate text-foreground">{e.label}</span>
              <span className="mono shrink-0 text-[11px] text-fg-muted">{e.time}</span>
              <Confidence value={e.confidence} />
            </Row>
          ))}
        </Section>

        {/* Timeline */}
        <Section n={3} title="Timeline" count={timeline.length}>
          <ol className="relative">
            <span className="absolute left-[104px] top-1 bottom-1 w-px bg-border-subtle" />
            {timeline.map((t, i) => (
              <li key={i} className="fade-in flex h-6 items-center gap-3 pl-4 pr-4 text-[12.5px] hover:bg-raised/40">
                <span className="mono w-20 shrink-0 text-[11px] text-fg-muted">{t.t}</span>
                <span className="relative z-10 h-1.5 w-1.5 shrink-0 rounded-full bg-fg-muted" />
                <SourceTag source={t.src} />
                <span className="min-w-0 flex-1 truncate text-foreground">{t.text}</span>
              </li>
            ))}
          </ol>
        </Section>

        {/* Metrics */}
        <Section n={4} title="Metrics" count={metrics.length}>
          <div className="grid grid-cols-2 gap-x-6 gap-y-2 px-4 md:grid-cols-4">
            {metrics.map((m) => (
              <div key={m.label} className="flex items-center justify-between gap-2 py-1">
                <div className="min-w-0">
                  <div className="text-micro">{m.label}</div>
                  <div className="mono text-[13px] text-fg-strong">{m.value}</div>
                  <div className={`mono text-[10.5px] ${m.trend === "up" ? "text-danger" : "text-info"}`}>{m.delta}</div>
                </div>
                <Sparkline data={m.spark} trend={m.trend} />
              </div>
            ))}
          </div>
        </Section>

        {/* Reasoning */}
        <Section n={5} title="Reasoning" count={reasoning.length}>
          <ol className="space-y-2 px-4">
            {reasoning.map((r, i) => (
              <li key={i} className="fade-in border-l border-border-subtle pl-3">
                <div className="text-[12.5px] text-foreground">
                  <span className="text-micro mr-2">Obs</span>
                  {r.obs}
                </div>
                <div className="mt-0.5 text-[12px] text-fg-muted">
                  <span className="text-micro mr-2">Ev</span>
                  <span className="mono">{r.ev.join(" · ")}</span>
                </div>
                <div className="mt-0.5 flex items-baseline gap-2 text-[12.5px] text-foreground">
                  <span className="text-micro">Inf</span>
                  <span className="min-w-0 flex-1">{r.inf}</span>
                  <Confidence value={r.conf} />
                </div>
              </li>
            ))}
            <li className="text-[12.5px] text-fg-muted pl-3">
              <span className="text-micro mr-2">Obs</span>
              Comparing pool exhaustion signature against INC-2011<span className="caret ml-0.5" />
            </li>
          </ol>
        </Section>

        {/* Hypotheses */}
        <Section n={6} title="Hypotheses" count={hypotheses.length}>
          {hypotheses.map((h, i) => (
            <div key={i} className="group relative">
              <div className="absolute inset-y-0 left-0 bg-accent/[0.06]" style={{ width: `${h.confidence * 100}%` }} />
              <Row>
                <span className="mono w-4 text-[11px] text-fg-muted">{String(i + 1).padStart(2, "0")}</span>
                <span className="relative z-10 min-w-0 flex-1 truncate text-foreground">{h.title}</span>
                <span className="relative z-10 mono text-[10.5px] text-fg-muted">
                  <span className="text-success">+{h.supporting}</span> · <span className="text-danger">−{h.refuting}</span>
                </span>
                <span className="relative z-10 mono text-[11.5px] text-foreground w-9 text-right">{Math.round(h.confidence * 100)}%</span>
              </Row>
            </div>
          ))}
        </Section>

        {/* Decision */}
        <Section n={7} title="Decision">
          <div className="mx-4 rounded-md border border-border bg-panel p-3">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <div className="text-micro">Recommendation</div>
                <div className="mt-0.5 text-[13px] text-fg-strong">Rollback deployment abc12f and restore connection pool to 20.</div>
              </div>
              <div className="shrink-0 text-right">
                <div className="text-micro">Confidence</div>
                <div className="mono text-[13px] text-accent">0.82</div>
              </div>
            </div>
            <div className="mt-3 grid grid-cols-3 gap-4 border-t border-border-subtle pt-3 text-[12px]">
              <div>
                <div className="text-micro">Risk</div>
                <div className="mt-0.5 flex items-center gap-1.5 text-foreground">
                  <span className="h-1.5 w-1.5 rounded-full bg-warning" /> Medium
                </div>
              </div>
              <div>
                <div className="text-micro">Blast radius</div>
                <div className="mt-0.5 text-foreground">payments-api · 12 pods</div>
              </div>
              <div>
                <div className="text-micro">Reversible</div>
                <div className="mt-0.5 text-foreground">Yes · ~90s rollback</div>
              </div>
            </div>
            <div className="mt-3 flex items-center gap-2">
              <button className="flex h-6 items-center gap-1.5 rounded border border-accent/40 bg-accent/10 px-2 text-[12px] text-accent hover:bg-accent/20">
                Approve <Kbd>⌘↵</Kbd>
              </button>
              <button className="flex h-6 items-center gap-1.5 rounded border border-border-subtle bg-raised/40 px-2 text-[12px] text-foreground hover:bg-raised">
                Alternatives <span className="mono text-fg-muted">· 2</span>
              </button>
            </div>
          </div>
        </Section>

        {/* Actions */}
        <Section n={8} title="Recommended Actions" count={actions.length}>
          {actions.map((a, i) => (
            <Row key={i}>
              <span className="grid h-3.5 w-3.5 shrink-0 place-items-center rounded-[3px] border border-border text-transparent transition-colors hover:border-accent" />
              <span className="min-w-0 flex-1 text-foreground">{a.text}</span>
              <SourceTag source={a.target} />
              {a.requires ? (
                <span className="mono text-[10.5px] text-warning">Requires: {a.requires}</span>
              ) : (
                <button className="mono text-[11px] text-accent opacity-0 transition-opacity group-hover:opacity-100">▶ Run</button>
              )}
            </Row>
          ))}
        </Section>

        {/* Summary */}
        <Section n={9} title="Summary" defaultOpen={false}>
          <div className="px-4 text-[12.5px] text-fg-muted">Auto-generated post-mortem draft will appear here once the incident is resolved.</div>
        </Section>

        <div className="h-16" />
      </div>
    </div>
  );
}
