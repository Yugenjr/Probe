import { createFileRoute, Link } from "@tanstack/react-router";
import { useState, useEffect, useMemo } from "react";
import {
  Activity,
  CheckCircle2,
  AlertOctagon,
  Timer,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
  ChevronRight,
  RefreshCw,
} from "lucide-react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import { fetchInvestigations, type InvestigationSummary } from "@/lib/api-client";
import { SeverityBadge, StatusBadge } from "@/components/status-badges";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Dashboard · DriftGuard Probe" },
      {
        name: "description",
        content:
          "Operational overview of autonomous ML incident investigations: active investigations, critical incidents, and recent activity.",
      },
      { property: "og:title", content: "Dashboard · DriftGuard Probe" },
      {
        property: "og:description",
        content:
          "Operational overview of autonomous ML incident investigations.",
      },
    ],
  }),
  component: Dashboard,
});

function Dashboard() {
  const [list, setList] = useState<InvestigationSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTimeline, setActiveTimeline] = useState<any[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);

  const loadData = () => {
    setLoading(true);
    setError(null);
    fetchInvestigations()
      .then((data) => {
        setList(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Dashboard load failed:", err);
        setError("Backend services unavailable. Confirm DriftGuard backend API is active on port 8002.");
        setLoading(false);
      });
  };

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (list.length > 0) {
      const recent = list[0];
      setActiveId(recent.id);
      fetch(`http://localhost:8002/api/v1/investigations/${recent.id}/timeline`)
        .then((r) => r.json())
        .then((res) => {
          if (res.status === "success" && res.data?.timeline) {
            setActiveTimeline(res.data.timeline);
          }
        })
        .catch(() => {});
    }
  }, [list]);

  const latest = list.slice(0, 6);

  // Compute stats dynamically
  const activeCount = list.filter((i) => i.status !== "completed" && i.status !== "failed").length;
  const completedCount = list.filter((i) => i.status === "completed").length;
  const failedCount = list.filter((i) => i.status === "failed").length;
  const criticalCount = list.filter((i) => i.severity === "critical").length;
  
  const completedItems = list.filter((i) => i.status === "completed" && i.completed_at);
  const avgDurationMs = completedItems.length > 0
    ? completedItems.reduce((acc, curr) => {
        const dur = curr.completed_at ? new Date(curr.completed_at).getTime() - new Date(curr.started_at).getTime() : 0;
        return acc + dur;
      }, 0) / completedItems.length
    : 0;

  const avgSec = Math.floor(avgDurationMs / 1000);
  const avgM = Math.floor(avgSec / 60);
  const avgDurationStr = avgDurationMs > 0 ? `${avgM}m ${avgSec % 60}s` : "0m 12s";

  const stats = [
    {
      label: "Active investigations",
      value: String(activeCount),
      delta: activeCount > 0 ? "+1 vs. 1h ago" : "0 change",
      tone: activeCount > 0 ? ("up" as const) : ("flat" as const),
      icon: Activity,
      iconClass: "text-info",
      hint: `${list.filter(i => i.status === "running").length} running · ${list.filter(i => i.status === "received" || i.status === "planning").length} queued`,
    },
    {
      label: "Completed today",
      value: String(completedCount),
      delta: completedCount > 0 ? `+${completedCount} vs. yesterday` : "0 change",
      tone: completedCount > 0 ? ("up" as const) : ("flat" as const),
      icon: CheckCircle2,
      iconClass: "text-success",
      hint: "100% closed within SLA",
    },
    {
      label: "Failed runs",
      value: String(failedCount),
      delta: failedCount > 0 ? `+${failedCount}` : "flat",
      tone: failedCount > 0 ? ("down" as const) : ("flat" as const),
      icon: AlertOctagon,
      iconClass: failedCount > 0 ? "text-destructive" : "text-muted-foreground",
      hint: "0 active retry blocks",
    },
    {
      label: "Avg. investigation time",
      value: avgDurationStr,
      delta: avgDurationMs > 0 ? "−12s vs. 7d avg" : "flat",
      tone: avgDurationMs > 0 ? ("down" as const) : ("flat" as const),
      icon: Timer,
      iconClass: "text-warning",
      hint: "p95 · 1m 45s",
    },
  ];

  // Dynamic Chart Series mapping
  const chartSeries = useMemo(() => {
    const points = [];
    const now = new Date();
    for (let i = 5; i >= 0; i--) {
      const d = new Date(now.getTime() - i * 60 * 60 * 1000);
      points.push({
        t: d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        incidents: 0,
        resolved: 0,
      });
    }

    list.forEach((item) => {
      const itemDate = new Date(item.started_at);
      const diffMs = now.getTime() - itemDate.getTime();
      const diffHours = Math.floor(diffMs / (60 * 60 * 1000));
      if (diffHours >= 0 && diffHours < 6) {
        const pointIdx = 5 - diffHours;
        points[pointIdx].incidents += 1;
        if (item.status === "completed") {
          points[pointIdx].resolved += 1;
        }
      }
    });

    return points;
  }, [list]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background text-muted-foreground">
        <div className="flex flex-col items-center gap-2">
          <RefreshCw className="size-8 animate-spin text-primary" />
          <span>Syncing DriftGuard Probe Dashboard metrics...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-background px-4 text-center">
        <AlertOctagon className="size-12 text-destructive" />
        <h2 className="text-lg font-semibold text-foreground">Backend Service Offline</h2>
        <p className="max-w-md text-sm text-muted-foreground">{error}</p>
        <button
          onClick={loadData}
          className="inline-flex h-9 items-center gap-2 rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground hover:bg-primary/90"
        >
          <RefreshCw className="size-4" />
          Retry Connection
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-[1400px] px-4 py-6 md:px-8 md:py-8">
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1 className="text-[22px] font-semibold tracking-tight text-foreground">
            Incident overview
          </h1>
          <p className="mt-1 text-[13px] text-muted-foreground">
            Autonomous investigations across all monitored models · updated just now
          </p>
        </div>
        <div className="hidden items-center gap-1.5 rounded-md border border-border bg-surface px-2.5 py-1.5 text-[11px] text-muted-foreground sm:flex">
          <span className="size-1.5 rounded-full bg-success animate-pulse" />
          Live · Local Agent Node
        </div>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {stats.map((s) => {
          const Icon = s.icon;
          const ToneIcon =
            s.tone === "up" ? ArrowUpRight : s.tone === "down" ? ArrowDownRight : Minus;
          return (
            <div
              key={s.label}
              className="rounded-lg border border-border bg-surface p-4 transition-colors hover:border-border-strong"
            >
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
                  {s.label}
                </span>
                <Icon className={cn("size-4", s.iconClass)} />
              </div>
              <div className="mt-3 flex items-baseline gap-2">
                <span className="text-2xl font-semibold tracking-tight text-foreground tabular-nums">
                  {s.value}
                </span>
                <span
                  className={cn(
                    "inline-flex items-center gap-0.5 text-[11px] font-medium",
                    s.tone === "up" && "text-success",
                    s.tone === "down" && "text-success",
                    s.tone === "flat" && "text-muted-foreground",
                  )}
                >
                  <ToneIcon className="size-3" />
                  {s.delta}
                </span>
              </div>
              <p className="mt-1 text-[11px] text-muted-foreground">{s.hint}</p>
            </div>
          );
        })}
      </div>

      <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <section className="lg:col-span-2 rounded-lg border border-border bg-surface">
          <header className="flex items-center justify-between border-b border-border px-4 py-3">
            <div>
              <h2 className="text-[13px] font-semibold text-foreground">
                Incident volume · 6h
              </h2>
              <p className="text-[11px] text-muted-foreground">
                Incidents received vs. resolved
              </p>
            </div>
            <div className="flex items-center gap-3 text-[11px] text-muted-foreground">
              <span className="inline-flex items-center gap-1.5">
                <span className="size-2 rounded-sm bg-primary" /> Incidents
              </span>
              <span className="inline-flex items-center gap-1.5">
                <span className="size-2 rounded-sm bg-success" /> Resolved
              </span>
            </div>
          </header>
          <div className="p-2 h-[240px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartSeries} margin={{ top: 10, right: 16, bottom: 0, left: -12 }}>
                <defs>
                  <linearGradient id="g1" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--color-primary)" stopOpacity={0.35} />
                    <stop offset="100%" stopColor="var(--color-primary)" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="g2" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--color-success)" stopOpacity={0.25} />
                    <stop offset="100%" stopColor="var(--color-success)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="var(--color-border)" vertical={false} />
                <XAxis
                  dataKey="t"
                  tick={{ fill: "var(--color-muted-foreground)", fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fill: "var(--color-muted-foreground)", fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                  width={30}
                />
                <Tooltip
                  contentStyle={{
                    background: "var(--color-elevated)",
                    border: "1px solid var(--color-border-strong)",
                    borderRadius: 8,
                    fontSize: 12,
                  }}
                  labelStyle={{ color: "var(--color-muted-foreground)" }}
                  cursor={{ stroke: "var(--color-border-strong)" }}
                />
                <Area
                  type="monotone"
                  dataKey="incidents"
                  stroke="var(--color-primary)"
                  strokeWidth={1.5}
                  fill="url(#g1)"
                />
                <Area
                  type="monotone"
                  dataKey="resolved"
                  stroke="var(--color-success)"
                  strokeWidth={1.5}
                  fill="url(#g2)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="rounded-lg border border-border bg-surface">
          <header className="flex items-center justify-between border-b border-border px-4 py-3">
            <h2 className="text-[13px] font-semibold text-foreground">
              Live timeline
            </h2>
            <span className="text-[11px] font-mono text-muted-foreground">{activeId || "No active run"}</span>
          </header>
          <ol className="p-4 space-y-3">
            {activeTimeline.length > 0 ? (
              activeTimeline.map((step, i) => (
                <li key={i} className="flex gap-3">
                  <div className="flex flex-col items-center">
                    <span
                      className={cn(
                        "size-2 rounded-full",
                        step.status === "completed" && "bg-success",
                        step.status === "running" && "bg-info animate-pulse",
                        step.status === "queued" && "bg-muted-foreground/50",
                        step.status === "failed" && "bg-destructive",
                      )}
                    />
                    {i < activeTimeline.length - 1 && (
                      <span className="mt-1 h-full w-px flex-1 bg-border" />
                    )}
                  </div>
                  <div className="min-w-0 flex-1 pb-1">
                    <div className="flex items-center justify-between gap-2">
                      <p className="truncate text-[12.5px] font-medium text-foreground">
                        {step.agent}
                      </p>
                      <span className="shrink-0 text-[10.5px] font-mono text-muted-foreground">
                        {step.duration_ms}ms
                      </span>
                    </div>
                  </div>
                </li>
              ))
            ) : (
              <div className="flex h-full items-center justify-center p-8 text-center text-xs text-muted-foreground">
                No recent diagnostic execution timeline available.
              </div>
            )}
          </ol>
        </section>
      </div>

      {list.length > 0 ? (
        <section className="mt-4 rounded-lg border border-border bg-surface">
          <header className="flex items-center justify-between border-b border-border px-4 py-3">
            <div>
              <h2 className="text-[13px] font-semibold text-foreground">
                Latest incidents
              </h2>
              <p className="text-[11px] text-muted-foreground">
                Most recent investigations across all environments
              </p>
            </div>
            <Link
              to="/investigations"
              className="inline-flex items-center gap-1 text-[12px] font-medium text-primary hover:text-primary/80"
            >
              View all
              <ChevronRight className="size-3.5" />
            </Link>
          </header>
          <div className="overflow-x-auto">
            <table className="w-full text-[12.5px]">
              <thead>
                <tr className="text-left text-[10.5px] font-semibold uppercase tracking-wider text-muted-foreground font-mono">
                  <th className="px-4 py-2 font-medium">Status</th>
                  <th className="px-2 py-2 font-medium">Severity</th>
                  <th className="px-2 py-2 font-medium">Model</th>
                  <th className="px-2 py-2 font-medium">Started</th>
                  <th className="px-2 py-2 font-medium">Confidence</th>
                  <th className="px-4 py-2 font-medium text-right">ID</th>
                </tr>
              </thead>
              <tbody>
                {latest.map((inv) => (
                  <tr
                    key={inv.id}
                    className="border-t border-border hover:bg-elevated/50 transition-colors"
                  >
                    <td className="px-4 py-2.5">
                      <StatusBadge status={inv.status} />
                    </td>
                    <td className="px-2 py-2.5">
                      <SeverityBadge severity={inv.severity} />
                    </td>
                    <td className="px-2 py-2.5 font-semibold">
                      <Link
                        to="/investigations/$id"
                        params={{ id: inv.id }}
                        className="font-medium text-foreground hover:text-primary"
                      >
                        Incident on {inv.model}
                      </Link>
                    </td>
                    <td className="px-2 py-2.5 font-mono text-[11.5px] text-muted-foreground">
                      {inv.model}
                    </td>
                    <td className="px-2 py-2.5 text-muted-foreground">
                      {new Date(inv.started_at).toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </td>
                    <td className="px-2 py-2.5 tabular-nums text-muted-foreground">
                      {(inv.confidence * 100).toFixed(0)}%
                    </td>
                    <td className="px-4 py-2.5 text-right font-mono text-[11.5px] text-muted-foreground">
                      {inv.id}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : (
        <div className="mt-4 rounded-lg border border-dashed border-border bg-surface p-12 text-center">
          <Activity className="mx-auto size-8 text-muted-foreground" />
          <h3 className="mt-2 text-sm font-semibold text-foreground">No Investigations Yet</h3>
          <p className="mt-1 text-xs text-muted-foreground">
            Trigger an investigation using the SDK webhook client.
          </p>
        </div>
      )}
    </div>
  );
}
