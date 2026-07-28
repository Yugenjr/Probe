import { createFileRoute, Link, useParams } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import {
  ArrowLeft,
  Download,
  FileDown,
  RefreshCw,
  ChevronDown,
  ChevronRight,
  Sparkles,
  FlaskConical,
  Lightbulb,
  FileText,
  ShieldAlert,
  AlertOctagon
} from "lucide-react";
import {
  fetchInvestigationDetails,
  fetchTimeline,
  fetchEvidence,
  fetchHypotheses,
  fetchEvaluation,
  fetchReport,
  type EvidenceItem,
  type HypothesisItem,
  type EvaluationResultItem,
  type ReportItem
} from "@/lib/api-client";
import { SeverityBadge, StatusBadge } from "@/components/status-badges";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/investigations/$id")({
  head: ({ params }) => ({
    meta: [
      { title: `${params.id} · Investigation · DriftGuard Probe` },
      {
        name: "description",
        content: `Autonomous investigation workspace for incident ${params.id}: timeline, evidence, hypotheses and recommendations.`,
      },
      {
        property: "og:title",
        content: `${params.id} · Investigation · DriftGuard Probe`,
      },
      {
        property: "og:description",
        content: "Investigation workspace with evidence, hypotheses and recommendations.",
      },
    ],
  }),
  component: InvestigationWorkspace,
});

function mapStatus(status: string) {
  status = status.toUpperCase();
  if (status === "COMPLETED") return "completed";
  if (status === "FAILED") return "failed";
  if (status === "CREATED" || status === "RECEIVED") return "queued";
  return "running";
}

function InvestigationWorkspace() {
  const { id } = useParams({ from: "/investigations/$id" });
  const [inv, setInv] = useState<any>(null);
  const [timelineSteps, setTimelineSteps] = useState<any[]>([]);
  const [evidenceList, setEvidenceList] = useState<any[]>([]);
  const [hypothesesList, setHypothesesList] = useState<any[]>([]);
  const [evaluation, setEvaluation] = useState<EvaluationResultItem | null>(null);
  const [report, setReport] = useState<ReportItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<"evidence" | "hypotheses" | "experiments" | "report">(
    "evidence",
  );

  const loadWorkspace = () => {
    setLoading(true);
    setError(null);

    Promise.all([
      fetchInvestigationDetails(id),
      fetchTimeline(id),
      fetchEvidence(id),
      fetchHypotheses(id),
      fetchEvaluation(id),
      fetchReport(id)
    ])
      .then(([details, timelineData, evidenceData, hypothesesData, evaluationData, reportData]) => {
        const hasHypothesis = hypothesesData && hypothesesData.length > 0;
        const confidence = hasHypothesis ? hypothesesData[0].likelihood_score : 0.85;

        setInv({
          id: details.session_id,
          incident: details.incident?.incident_id ? `Incident on ${details.incident.model_id} (${details.incident.incident_id})` : `Incident on ${details.incident?.model_id || "unknown"}`,
          model: details.incident?.model_id || "unknown",
          modelVersion: details.incident?.model_version || "latest",
          severity: (details.incident?.severity || "medium").toLowerCase(),
          status: mapStatus(details.status),
          startedAt: details.started_at,
          completedAt: details.completed_at,
          durationMs: details.completed_at
            ? new Date(details.completed_at).getTime() - new Date(details.started_at).getTime()
            : null,
          confidence: confidence,
          recommendation: details.remediation_plan?.intervention_type || "—",
          assignee: "probe-agent",
          environment: "production",
          region: "us-east-1",
          rawSession: details
        });

        setTimelineSteps(timelineData.map((t: any) => ({
          key: t.agent,
          label: t.agent,
          status: t.status === "completed" ? "done" : (t.status === "failed" ? "failed" : (t.status === "running" ? "running" : "queued")),
          startedAt: new Date(t.started_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
          durationMs: t.duration_ms,
          detail: t.agent === "Webhook Ingestion" ? "DriftGuard alert ingested." : `${t.agent} execution completed.`
        })));

        setEvidenceList(evidenceData.universal_evidence.map((ev: any) => ({
          id: ev.evidence_id,
          title: ev.summary,
          confidence: ev.confidence_weight,
          explanation: ev.summary,
          metrics: [
            { label: "Observed Distance", value: String(ev.observed_distance) },
            { label: "Threshold", value: String(ev.alarm_threshold) },
            { label: "Feature", value: String(ev.feature_name) },
            { label: "Algorithm", value: String(ev.distance_algorithm) }
          ],
          metadata: ev
        })));

        setHypothesesList(hypothesesData.map((h: any, idx: number) => ({
          id: h.hypothesis_id || `H-0${idx+1}`,
          title: h.title,
          confidence: h.confidence ?? h.likelihood_score,
          supporting: h.supporting_evidence_ids || [],
          weaknesses: h.weaknesses || []
        })));

        setEvaluation(evaluationData);
        setReport(reportData);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Workspace load failed:", err);
        setError("Network error connecting to DriftGuard Backend or investigation not found.");
        setLoading(false);
      });
  };

  useEffect(() => {
    loadWorkspace();
  }, [id]);

  if (loading && !inv) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background text-muted-foreground">
        <div className="flex flex-col items-center gap-2">
          <RefreshCw className="size-8 animate-spin text-primary" />
          <span>Loading investigation workflow workspace...</span>
        </div>
      </div>
    );
  }

  if (error && !inv) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-background px-4 text-center">
        <AlertOctagon className="size-12 text-destructive" />
        <h2 className="text-lg font-semibold text-foreground">Workspace Offline</h2>
        <p className="max-w-md text-sm text-muted-foreground">{error}</p>
        <button
          onClick={loadWorkspace}
          className="inline-flex h-9 items-center gap-2 rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground hover:bg-primary/90"
        >
          <RefreshCw className="size-4" />
          Retry Connection
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col">
      {/* Header */}
      <div className="border-b border-border bg-surface/50">
        <div className="mx-auto max-w-[1600px] px-4 py-4 md:px-8">
          <Link
            to="/investigations"
            className="inline-flex items-center gap-1 text-[12px] text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft className="size-3.5" />
            All investigations
          </Link>
          <div className="mt-3 flex flex-wrap items-start justify-between gap-4">
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-mono text-[11.5px] text-muted-foreground">
                  {inv.id}
                </span>
                <SeverityBadge severity={inv.severity} />
                <StatusBadge status={inv.status} />
              </div>
              <h1 className="mt-2 text-[20px] font-semibold tracking-tight text-foreground">
                {inv.incident}
              </h1>
              <div className="mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-1 text-[12px] text-muted-foreground">
                <span>
                  Model{" "}
                  <span className="font-mono text-foreground">{inv.model}</span>
                  <span className="ml-1 text-border-strong">
                    · {inv.modelVersion}
                  </span>
                </span>
                <span className="text-border-strong">·</span>
                <span>
                  Started{" "}
                  <span className="text-foreground">
                    {new Date(inv.startedAt).toLocaleString([], {
                      dateStyle: "medium",
                      timeStyle: "short",
                    })}
                  </span>
                </span>
                <span className="text-border-strong">·</span>
                <span>
                  Env{" "}
                  <span className="text-foreground capitalize">
                    {inv.environment}
                  </span>
                </span>
                <span className="text-border-strong">·</span>
                <span>
                  Region <span className="text-foreground">{inv.region}</span>
                </span>
              </div>
            </div>
            <div className="flex items-center gap-1.5">
              <button
                onClick={loadWorkspace}
                className="inline-flex h-8 items-center gap-1.5 rounded-md border border-border bg-surface px-2.5 text-[12px] font-medium text-foreground hover:border-border-strong"
              >
                <RefreshCw className="size-3.5 text-muted-foreground" />
                Refresh
              </button>
              <button
                onClick={() => {
                  const blob = new Blob([JSON.stringify(inv.rawSession, null, 2)], { type: "application/json" });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement("a");
                  a.href = url;
                  a.download = `${inv.id}.json`;
                  a.click();
                  URL.revokeObjectURL(url);
                }}
                className="inline-flex h-8 items-center gap-1.5 rounded-md border border-border bg-surface px-2.5 text-[12px] font-medium text-foreground hover:border-border-strong"
              >
                <FileDown className="size-3.5 text-muted-foreground" />
                Download JSON
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="mx-auto grid w-full max-w-[1600px] grid-cols-1 gap-4 px-4 py-6 md:px-8 md:py-6 lg:grid-cols-[240px_minmax(0,1fr)_300px]">
        {/* Left: timeline */}
        <aside className="lg:sticky lg:top-[72px] lg:self-start">
          <div className="rounded-lg border border-border bg-surface">
            <header className="border-b border-border px-3 py-2.5">
              <h2 className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                Investigation timeline
              </h2>
            </header>
            <ol className="p-3 space-y-2.5">
              {timelineSteps.map((step, i) => (
                <li key={step.key} className="flex gap-2.5">
                  <div className="flex flex-col items-center">
                    <span
                      className={cn(
                        "mt-1 size-2 rounded-full ring-2",
                        step.status === "done" && "bg-success ring-success/20",
                        step.status === "running" &&
                          "bg-info ring-info/20 animate-pulse",
                        step.status === "queued" &&
                          "bg-muted-foreground/40 ring-transparent",
                        step.status === "failed" &&
                          "bg-destructive ring-destructive/20",
                      )}
                    />
                    {i < timelineSteps.length - 1 && (
                      <span className="mt-1 h-full w-px flex-1 bg-border" />
                    )}
                  </div>
                  <div className="min-w-0 flex-1 pb-1">
                    <p
                      className={cn(
                        "truncate text-[12px] font-medium",
                        step.status === "queued"
                          ? "text-muted-foreground"
                          : "text-foreground",
                      )}
                    >
                      {step.label}
                    </p>
                    <div className="mt-0.5 flex items-center gap-1.5 text-[10.5px] font-mono text-muted-foreground">
                      <span>{step.startedAt}</span>
                      {step.durationMs != null && (
                        <>
                          <span className="text-border-strong">·</span>
                          <span>{step.durationMs}ms</span>
                        </>
                      )}
                    </div>
                    {step.detail && (
                      <p className="mt-1 text-[11px] leading-relaxed text-muted-foreground">
                        {step.detail}
                      </p>
                    )}
                  </div>
                </li>
              ))}
            </ol>
          </div>
        </aside>

        {/* Center: tabs */}
        <section className="min-w-0">
          <div className="flex items-center gap-1 border-b border-border">
            {(
              [
                { k: "evidence", l: "Evidence", i: Sparkles, c: evidenceList.length },
                { k: "hypotheses", l: "Hypotheses", i: Lightbulb, c: hypothesesList.length },
                { k: "experiments", l: "Recommendations", i: FlaskConical, c: evaluation?.recommended_actions?.length || 0 },
                { k: "report", l: "Report", i: FileText },
              ] as const
            ).map((t) => {
              const Icon = t.i;
              const active = tab === t.k;
              return (
                <button
                  key={t.k}
                  onClick={() => setTab(t.k)}
                  className={cn(
                    "relative inline-flex items-center gap-1.5 px-3 py-2.5 text-[12.5px] font-medium transition-colors",
                    active
                      ? "text-foreground"
                      : "text-muted-foreground hover:text-foreground",
                  )}
                >
                  <Icon className="size-3.5" />
                  {t.l}
                  {"c" in t && t.c != null && (
                    <span className="ml-0.5 rounded bg-surface-2 px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">
                      {t.c}
                    </span>
                  )}
                  {active && (
                    <span className="absolute inset-x-2 -bottom-px h-px bg-primary" />
                  )}
                </button>
              );
            })}
          </div>

          <div className="mt-4 space-y-3">
            {tab === "evidence" && (
              evidenceList.length > 0 ? (
                evidenceList.map((e) => <EvidenceCard key={e.id} evidence={e} />)
              ) : (
                <div className="text-xs text-muted-foreground p-8 text-center">
                  No evidence gathered yet.
                </div>
              )
            )}
            {tab === "hypotheses" && (
              hypothesesList.length > 0 ? (
                hypothesesList.map((h) => <HypothesisCard key={h.id} h={h} />)
              ) : (
                <div className="text-xs text-muted-foreground p-8 text-center">
                  No hypotheses synthesized yet.
                </div>
              )
            )}
            {tab === "experiments" && (
              evaluation?.recommended_actions && evaluation.recommended_actions.length > 0 ? (
                evaluation.recommended_actions.map((r: any, idx: number) => (
                  <div key={idx} className="rounded-lg border border-border bg-surface p-4">
                    <div className="flex items-start justify-between gap-4">
                      <div className="min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-[10.5px] text-muted-foreground">
                            REC-0{idx+1}
                          </span>
                          <span className="inline-flex items-center rounded-md border border-destructive/30 bg-destructive/10 px-1.5 py-0 text-[10px] font-semibold text-destructive">
                            {r.priority}
                          </span>
                          <span className="inline-flex items-center rounded-md border border-success/30 bg-success/10 px-1.5 py-0 text-[10px] font-medium capitalize text-success">
                            risk · {r.estimated_risk}
                          </span>
                        </div>
                        <p className="mt-0.5 text-[13.5px] font-medium text-foreground">
                          {r.action}
                        </p>
                        <p className="mt-1 text-[12px] leading-relaxed text-muted-foreground">
                          {r.reason}
                        </p>
                      </div>
                    </div>
                    <div className="mt-3 grid grid-cols-3 gap-2 border-t border-border pt-3">
                      <MiniStat label="Est. time" value={r.estimated_time} />
                      <MiniStat label="Priority" value={r.priority} />
                      <MiniStat label="Risk" value={r.estimated_risk} className="capitalize" />
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-xs text-muted-foreground p-8 text-center">
                  No evaluation recommendations generated yet.
                </div>
              )
            )}
            {tab === "report" && <ReportPanel markdown={report?.markdown_content} />}
          </div>
        </section>

        {/* Right: summary */}
        <aside className="lg:sticky lg:top-[72px] lg:self-start">
          <div className="space-y-3">
            <SummaryCard title="Incident summary">
              <SummaryRow label="Incident">{inv.incident}</SummaryRow>
              <SummaryRow label="Detected by">DriftGuard Alert Ingestion</SummaryRow>
              <SummaryRow label="Assignee">
                <span className="font-mono">{inv.assignee}</span>
              </SummaryRow>
              <SummaryRow label="Window">last 24h</SummaryRow>
            </SummaryCard>

            <SummaryCard title="Model">
              <SummaryRow label="Name">
                <span className="font-mono">{inv.model}</span>
              </SummaryRow>
              <SummaryRow label="Version">
                <span className="font-mono">{inv.modelVersion}</span>
              </SummaryRow>
              <SummaryRow label="Region">{inv.region}</SummaryRow>
              <SummaryRow label="Environment">
                <span className="capitalize">{inv.environment}</span>
              </SummaryRow>
            </SummaryCard>

            <div className="rounded-lg border border-border bg-surface p-4">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                  Confidence
                </span>
                <ShieldAlert className="size-3.5 text-muted-foreground" />
              </div>
              <div className="mt-2 flex items-baseline gap-2">
                <span className="text-2xl font-semibold tabular-nums text-foreground">
                  {(inv.confidence * 100).toFixed(0)}%
                </span>
                <span className="text-[11px] text-muted-foreground">
                  top hypothesis
                </span>
              </div>
              <div className="mt-3 h-1 overflow-hidden rounded-full bg-border">
                <div
                  className="h-full bg-primary"
                  style={{ width: `${inv.confidence * 100}%` }}
                />
              </div>
              <p className="mt-3 text-[11.5px] leading-relaxed text-muted-foreground">
                Diagnostic confidence calculated dynamically across formulated root-cause candidates.
              </p>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}

function SummaryCard({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-lg border border-border bg-surface">
      <header className="border-b border-border px-3 py-2.5">
        <h2 className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
          {title}
        </h2>
      </header>
      <dl className="p-3 space-y-2">{children}</dl>
    </div>
  );
}

function SummaryRow({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex items-start justify-between gap-3 text-[12px]">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className="text-right text-foreground min-w-0 break-words font-medium">
        {children}
      </dd>
    </div>
  );
}

function EvidenceCard({ evidence }: { evidence: any }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="rounded-lg border border-border bg-surface">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-start gap-3 px-4 py-3 text-left"
      >
        <span className="mt-0.5 shrink-0">
          {open ? (
            <ChevronDown className="size-4 text-muted-foreground" />
          ) : (
            <ChevronRight className="size-4 text-muted-foreground" />
          )}
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className="font-mono text-[10.5px] text-muted-foreground">
              {evidence.id}
            </span>
            <span className="text-[10.5px] text-border-strong">·</span>
            <span className="text-[10.5px] font-medium text-info font-mono">
              {(evidence.confidence * 100).toFixed(0)}% confidence
            </span>
          </div>
          <p className="mt-0.5 text-[13.5px] font-medium text-foreground">
            {evidence.title}
          </p>
        </div>
      </button>
      {open && (
        <div className="border-t border-border px-4 py-4 space-y-4">
          <p className="text-[12.5px] leading-relaxed text-muted-foreground">
            {evidence.explanation}
          </p>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
            {evidence.metrics.map((m: any) => (
              <div
                key={m.label}
                className="rounded-md border border-border bg-background/40 p-2.5 font-mono"
              >
                <div className="text-[10.5px] uppercase tracking-wider text-muted-foreground font-sans">
                  {m.label}
                </div>
                <div className="mt-1 flex items-baseline gap-1.5">
                  <span className="text-[15px] font-semibold tabular-nums text-foreground">
                    {m.value}
                  </span>
                </div>
              </div>
            ))}
          </div>
          <div>
            <div className="text-[10.5px] font-semibold uppercase tracking-wider text-muted-foreground mb-1.5 font-mono">
              Raw metadata
            </div>
            <pre className="overflow-x-auto rounded-md border border-border bg-background/60 p-3 text-[11.5px] leading-relaxed font-mono text-muted-foreground">
              {JSON.stringify(evidence.metadata, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}

function HypothesisCard({ h }: { h: any }) {
  const pct = Math.round(h.confidence * 100);
  const tone =
    pct >= 70 ? "bg-primary" : pct >= 40 ? "bg-warning" : "bg-muted-foreground";
  return (
    <div className="rounded-lg border border-border bg-surface p-4">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <span className="font-mono text-[10.5px] text-muted-foreground">
              {h.id}
            </span>
          </div>
          <p className="mt-0.5 text-[13.5px] font-medium text-foreground">
            {h.title}
          </p>
        </div>
        <div className="shrink-0 text-right">
          <div className="text-[10.5px] uppercase tracking-wider text-muted-foreground">
            Confidence
          </div>
          <div className="mt-0.5 text-[15px] font-semibold tabular-nums text-foreground font-mono">
            {pct}%
          </div>
        </div>
      </div>
      <div className="mt-3 h-1 overflow-hidden rounded-full bg-border">
        <div className={`h-full ${tone}`} style={{ width: `${pct}%` }} />
      </div>
      <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div>
          <div className="text-[10.5px] font-semibold uppercase tracking-wider text-success mb-1.5 font-mono">
            Supporting evidence
          </div>
          <ul className="space-y-1">
            {h.supporting.map((s: string, i: number) => (
              <li key={i} className="flex gap-1.5 text-[12px] text-muted-foreground">
                <span className="mt-1.5 size-1 shrink-0 rounded-full bg-success" />
                <span className="font-mono">{s}</span>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <div className="text-[10.5px] font-semibold uppercase tracking-wider text-warning mb-1.5 font-mono">
            Weaknesses
          </div>
          <ul className="space-y-1">
            {h.weaknesses.map((s: string, i: number) => (
              <li key={i} className="flex gap-1.5 text-[12px] text-muted-foreground">
                <span className="mt-1.5 size-1 shrink-0 rounded-full bg-warning" />
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

function MiniStat({
  label,
  value,
  className,
}: {
  label: string;
  value: string;
  className?: string;
}) {
  return (
    <div>
      <div className="text-[10px] uppercase tracking-wider text-muted-foreground">
        {label}
      </div>
      <div className={cn("mt-0.5 text-[12.5px] font-medium text-foreground", className)}>
        {value}
      </div>
    </div>
  );
}

function ReportPanel({ markdown }: { markdown?: string }) {
  if (!markdown) {
    return (
      <article className="rounded-lg border border-border bg-surface px-6 py-6 md:px-8 md:py-8">
        <p className="text-[10.5px] font-semibold uppercase tracking-wider text-muted-foreground">
          No report generated yet.
        </p>
      </article>
    );
  }

  const parsed = markdown.split("\n").map((line, idx) => {
    if (line.startsWith("# ")) return <h1 key={idx} className="text-2xl font-bold mt-6 mb-3 text-foreground border-b border-border pb-2">{line.slice(2)}</h1>;
    if (line.startsWith("## ")) return <h2 key={idx} className="text-xl font-bold mt-5 mb-2 text-foreground">{line.slice(3)}</h2>;
    if (line.startsWith("### ")) return <h3 key={idx} className="text-lg font-bold mt-4 mb-2 text-foreground">{line.slice(4)}</h3>;
    if (line.startsWith("- ")) return <li key={idx} className="ml-4 list-disc text-muted-foreground my-1">{line.slice(2)}</li>;
    if (line.trim() === "") return <div key={idx} className="h-2" />;
    return <p key={idx} className="my-2 leading-relaxed text-muted-foreground">{line}</p>;
  });

  const handleCopy = () => {
    navigator.clipboard.writeText(markdown);
  };

  const handleExport = () => {
    const blob = new Blob([markdown], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `driftguard-report.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <article className="rounded-lg border border-border bg-surface px-6 py-6 md:px-8 md:py-8">
      <div className="prose prose-invert max-w-none prose-headings:tracking-tight prose-headings:text-foreground prose-strong:text-foreground">
        {parsed}
      </div>
      <div className="mt-6 flex items-center gap-2 border-t border-border pt-4">
        <button
          onClick={handleCopy}
          className="inline-flex h-8 items-center gap-1.5 rounded-md border border-border bg-background px-2.5 text-[12px] font-medium text-foreground hover:border-border-strong"
        >
          Copy Report
        </button>
        <button
          onClick={handleExport}
          className="inline-flex h-8 items-center gap-1.5 rounded-md border border-border bg-background px-2.5 text-[12px] font-medium text-foreground hover:border-border-strong"
        >
          <FileDown className="size-3.5" /> Export Markdown
        </button>
      </div>
    </article>
  );
}
