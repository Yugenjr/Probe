import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo, useState, useEffect } from "react";
import { Search, SlidersHorizontal, Download, AlertOctagon, RefreshCw } from "lucide-react";
import { fetchInvestigations, type InvestigationSummary } from "@/lib/api-client";
import { SeverityBadge, StatusBadge } from "@/components/status-badges";

export const Route = createFileRoute("/investigations/")({
  head: () => ({
    meta: [
      { title: "Investigations · DriftGuard Probe" },
      {
        name: "description",
        content:
          "Searchable log of all autonomous ML incident investigations with severity, status, model and recommendation.",
      },
      { property: "og:title", content: "Investigations · DriftGuard Probe" },
      {
        property: "og:description",
        content: "All autonomous ML incident investigations.",
      },
    ],
  }),
  component: InvestigationsPage,
});

function formatDuration(ms: number | null) {
  if (!ms) return "—";
  const s = Math.floor(ms / 1000);
  const m = Math.floor(s / 60);
  return `${m}m ${s % 60}s`;
}

function InvestigationsPage() {
  const [q, setQ] = useState("");
  const [severity, setSeverity] = useState<string>("all");
  const [status, setStatus] = useState<string>("all");
  const [list, setList] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = () => {
    setLoading(true);
    setError(null);
    fetchInvestigations()
      .then((data) => {
        const mapped = data.map((item) => ({
          id: item.id,
          incident: `Incident on ${item.model}`,
          model: item.model,
          modelVersion: "latest",
          region: "us-east-1",
          severity: item.severity,
          status: item.status,
          startedAt: item.started_at,
          completedAt: item.completed_at,
          durationMs: item.completed_at
            ? new Date(item.completed_at).getTime() - new Date(item.started_at).getTime()
            : null,
          confidence: item.confidence,
          recommendation: item.status === "completed" ? "Remediation Proposal Formulated" : (item.status === "failed" ? "Investigation Aborted" : "Running diagnostic Pipeline...")
        }));
        setList(mapped);
        setLoading(false);
      })
      .catch((err) => {
        console.error("List Page load failed:", err);
        setError("Backend services offline. Failed to retrieve investigations log.");
        setLoading(false);
      });
  };

  useEffect(() => {
    loadData();
  }, []);

  const rows = useMemo(() => {
    return list.filter((i) => {
      const matches =
        q === "" ||
        i.incident.toLowerCase().includes(q.toLowerCase()) ||
        i.model.toLowerCase().includes(q.toLowerCase()) ||
        i.id.toLowerCase().includes(q.toLowerCase());
      const sev = severity === "all" || i.severity === severity;
      const st = status === "all" || i.status === status;
      return matches && sev && st;
    });
  }, [q, severity, status, list]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background text-muted-foreground">
        <div className="flex flex-col items-center gap-2">
          <RefreshCw className="size-8 animate-spin text-primary" />
          <span>Syncing DriftGuard Probe investigations log...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-background px-4 text-center">
        <AlertOctagon className="size-12 text-destructive" />
        <h2 className="text-lg font-semibold text-foreground">Sync Failed</h2>
        <p className="max-w-md text-sm text-muted-foreground">{error}</p>
        <button
          onClick={loadData}
          className="inline-flex h-9 items-center gap-2 rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground hover:bg-primary/90"
        >
          <RefreshCw className="size-4" />
          Retry Sync
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-[1400px] px-4 py-6 md:px-8 md:py-8">
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1 className="text-[22px] font-semibold tracking-tight text-foreground">
            Investigations
          </h1>
          <p className="mt-1 text-[13px] text-muted-foreground">
            {rows.length} of {list.length} · updated just now
          </p>
        </div>
        <button className="inline-flex h-8 items-center gap-1.5 rounded-md border border-border bg-surface px-2.5 text-[12px] font-medium text-foreground hover:border-border-strong">
          <Download className="size-3.5 text-muted-foreground" />
          Export
        </button>
      </div>

      <div className="mt-5 flex flex-wrap items-center gap-2">
        <div className="relative flex-1 min-w-[220px] max-w-md">
          <Search className="pointer-events-none absolute left-2.5 top-1/2 size-3.5 -translate-y-1/2 text-muted-foreground" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search incident, model, or ID…"
            className="h-9 w-full rounded-md border border-border bg-surface pl-8 pr-3 text-[13px] text-foreground placeholder:text-muted-foreground focus:border-primary/60 focus:outline-none focus:ring-2 focus:ring-primary/20"
          />
        </div>
        <FilterSelect
          value={severity}
          onChange={setSeverity}
          options={[
            { v: "all", l: "All severities" },
            { v: "critical", l: "Critical" },
            { v: "high", l: "High" },
            { v: "medium", l: "Medium" },
            { v: "low", l: "Low" },
          ]}
        />
        <FilterSelect
          value={status}
          onChange={setStatus}
          options={[
            { v: "all", l: "All statuses" },
            { v: "running", l: "Running" },
            { v: "completed", l: "Completed" },
            { v: "failed", l: "Failed" },
            { v: "queued", l: "Queued" },
          ]}
        />
        <button className="inline-flex h-9 items-center gap-1.5 rounded-md border border-border bg-surface px-2.5 text-[12px] font-medium text-muted-foreground hover:border-border-strong hover:text-foreground">
          <SlidersHorizontal className="size-3.5" />
          More filters
        </button>
      </div>

      <div className="mt-4 overflow-hidden rounded-lg border border-border bg-surface">
        <div className="overflow-x-auto">
          <table className="w-full text-[12.5px]">
            <thead className="bg-surface-2/60">
              <tr className="text-left text-[10.5px] font-semibold uppercase tracking-wider text-muted-foreground font-mono">
                <th className="px-4 py-2.5 font-medium">Status</th>
                <th className="px-2 py-2.5 font-medium">Severity</th>
                <th className="px-2 py-2.5 font-medium">Model</th>
                <th className="px-2 py-2.5 font-medium">Incident</th>
                <th className="px-2 py-2.5 font-medium">Started</th>
                <th className="px-2 py-2.5 font-medium">Duration</th>
                <th className="px-2 py-2.5 font-medium">Confidence</th>
                <th className="px-4 py-2.5 font-medium">Recommendation</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((inv) => (
                <tr
                  key={inv.id}
                  className="group border-t border-border transition-colors hover:bg-elevated/50"
                >
                  <td className="px-4 py-2.5">
                    <StatusBadge status={inv.status} />
                  </td>
                  <td className="px-2 py-2.5">
                    <SeverityBadge severity={inv.severity} />
                  </td>
                  <td className="px-2 py-2.5 font-mono text-[11.5px] text-muted-foreground">
                    <div className="text-foreground">{inv.model}</div>
                    <div className="text-[10.5px] text-muted-foreground">
                      {inv.modelVersion} · {inv.region}
                    </div>
                  </td>
                  <td className="px-2 py-2.5">
                    <Link
                      to="/investigations/$id"
                      params={{ id: inv.id }}
                      className="font-medium text-foreground hover:text-primary"
                    >
                      {inv.incident}
                    </Link>
                    <div className="text-[10.5px] font-mono text-muted-foreground">
                      {inv.id}
                    </div>
                  </td>
                  <td className="px-2 py-2.5 text-muted-foreground whitespace-nowrap">
                    {new Date(inv.startedAt).toLocaleString([], {
                      month: "short",
                      day: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </td>
                  <td className="px-2 py-2.5 tabular-nums text-muted-foreground">
                    {formatDuration(inv.durationMs)}
                  </td>
                  <td className="px-2 py-2.5 tabular-nums">
                    <ConfidenceBar value={inv.confidence} />
                  </td>
                  <td className="px-4 py-2.5 text-muted-foreground max-w-[260px] truncate">
                    {inv.recommendation}
                  </td>
                </tr>
              ))}
              {rows.length === 0 && (
                <tr>
                  <td colSpan={8} className="px-4 py-16 text-center">
                    <div className="mx-auto max-w-sm">
                      <div className="mx-auto flex size-10 items-center justify-center rounded-full border border-border bg-surface-2 text-muted-foreground">
                        <Search className="size-4" />
                      </div>
                      <p className="mt-3 text-[13px] font-medium text-foreground">
                        No investigations match your filters
                      </p>
                      <p className="mt-1 text-[12px] text-muted-foreground">
                        Try clearing filters or broadening your search.
                      </p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function FilterSelect({
  value,
  onChange,
  options,
}: {
  value: string;
  onChange: (v: string) => void;
  options: { v: string; l: string }[];
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="h-9 rounded-md border border-border bg-surface px-2.5 text-[12px] text-foreground focus:border-primary/60 focus:outline-none focus:ring-2 focus:ring-primary/20"
    >
      {options.map((o) => (
        <option key={o.v} value={o.v}>
          {o.l}
        </option>
      ))}
    </select>
  );
}

function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const tone =
    pct >= 80
      ? "bg-success"
      : pct >= 60
        ? "bg-info"
        : pct >= 40
          ? "bg-warning"
          : "bg-destructive";
  return (
    <div className="flex items-center gap-2">
      <div className="h-1 w-16 overflow-hidden rounded-full bg-border">
        <div className={`h-full ${tone}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-[11px] text-muted-foreground">{pct}%</span>
    </div>
  );
}
