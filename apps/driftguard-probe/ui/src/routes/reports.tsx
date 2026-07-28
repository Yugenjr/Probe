import { createFileRoute } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { FileText, Download, Calendar, RefreshCw, AlertOctagon } from "lucide-react";
import { fetchInvestigations, type InvestigationSummary } from "@/lib/api-client";
import { SeverityBadge } from "@/components/status-badges";

export const Route = createFileRoute("/reports")({
  head: () => ({
    meta: [
      { title: "Reports · DriftGuard Probe" },
      {
        name: "description",
        content:
          "Exported investigation reports with root cause, evidence and recommendations.",
      },
      { property: "og:title", content: "Reports · DriftGuard Probe" },
      { property: "og:description", content: "Exported investigation reports." },
    ],
  }),
  component: ReportsPage,
});

function ReportsPage() {
  const [list, setList] = useState<InvestigationSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = () => {
    setLoading(true);
    setError(null);
    fetchInvestigations()
      .then((data) => {
        setList(data.filter((i) => i.status === "completed"));
        setLoading(false);
      })
      .catch((err) => {
        console.error("Reports Page load failed:", err);
        setError("Backend services offline. Failed to retrieve completed investigation reports.");
        setLoading(false);
      });
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background text-muted-foreground">
        <div className="flex flex-col items-center gap-2">
          <RefreshCw className="size-8 animate-spin text-primary" />
          <span>Syncing DriftGuard Probe reports...</span>
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
            Reports
          </h1>
          <p className="mt-1 text-[13px] text-muted-foreground">
            {list.length} completed investigations with exportable reports
          </p>
        </div>
      </div>

      {list.length > 0 ? (
        <div className="mt-6 grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
          {list.map((r) => (
            <article
              key={r.id}
              className="group flex flex-col rounded-lg border border-border bg-surface p-4 transition-colors hover:border-border-strong"
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-[10.5px] text-muted-foreground">
                  {r.id}
                </span>
                <SeverityBadge severity={r.severity} />
              </div>
              <h3 className="mt-2 text-[14px] font-semibold text-foreground line-clamp-2">
                Incident on {r.model}
              </h3>
              <p className="mt-1.5 text-[12px] text-muted-foreground line-clamp-2">
                Confidence of diagnostic outcome: {(r.confidence * 100).toFixed(0)}%
              </p>
              <div className="mt-3 flex items-center gap-3 text-[11px] text-muted-foreground">
                <span className="inline-flex items-center gap-1">
                  <Calendar className="size-3" />
                  {r.completed_at ? new Date(r.completed_at).toLocaleDateString([], {
                    month: "short",
                    day: "numeric",
                  }) : "—"}
                </span>
                <span className="text-border-strong">·</span>
                <span className="font-mono">{r.model}</span>
              </div>
              <div className="mt-4 flex items-center justify-between border-t border-border pt-3">
                <span className="inline-flex items-center gap-1 text-[11px] text-muted-foreground">
                  <FileText className="size-3" />
                  Full report
                </span>
                <button className="inline-flex h-7 items-center gap-1 rounded-md border border-border bg-background px-2 text-[11px] font-medium text-foreground hover:border-border-strong">
                  <Download className="size-3" />
                  Export
                </button>
              </div>
            </article>
          ))}
        </div>
      ) : (
        <div className="mt-6 rounded-lg border border-dashed border-border bg-surface p-12 text-center">
          <FileText className="mx-auto size-8 text-muted-foreground" />
          <h3 className="mt-2 text-sm font-semibold text-foreground">No Exportable Reports</h3>
          <p className="mt-1 text-xs text-muted-foreground">
            Complete an investigation to generate and export markdown reports here.
          </p>
        </div>
      )}
    </div>
  );
}
