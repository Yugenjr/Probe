import { createFileRoute } from "@tanstack/react-router";
import { BookOpen, ArrowUpRight, Search } from "lucide-react";
import { useState } from "react";

export const Route = createFileRoute("/knowledge-base")({
  head: () => ({
    meta: [
      { title: "Knowledge Base · DriftGuard Probe" },
      {
        name: "description",
        content:
          "Playbooks, past investigations and remediation patterns learned by DriftGuard Probe.",
      },
      { property: "og:title", content: "Knowledge Base · DriftGuard Probe" },
      { property: "og:description", content: "Investigation playbooks and patterns." },
    ],
  }),
  component: KBPage,
});

const articles = [
  {
    id: "KB-101",
    category: "Playbook",
    title: "Diagnosing PSI drift on embedding features",
    excerpt:
      "How Probe correlates upstream deploy timestamps with per-dimension PSI to isolate normalization regressions.",
    reads: 148,
    updated: "2 days ago",
  },
  {
    id: "KB-102",
    category: "Pattern",
    title: "Latency regressions after autoscaler events",
    excerpt:
      "Recurring pattern: cold-start on newly-provisioned replicas skews p99 for the first ~90s. Mitigation: min-replicas tuning.",
    reads: 92,
    updated: "5 days ago",
  },
  {
    id: "KB-103",
    category: "Playbook",
    title: "Calibration drift: ECE > 0.15 response",
    excerpt:
      "Decision tree for choosing between Platt scaling, isotonic regression and full retrain.",
    reads: 214,
    updated: "1 week ago",
  },
  {
    id: "KB-104",
    category: "Runbook",
    title: "Rolling back a feature pipeline safely",
    excerpt:
      "Preconditions, ordering constraints and backfill considerations when reverting an upstream feature job.",
    reads: 76,
    updated: "1 week ago",
  },
  {
    id: "KB-105",
    category: "Pattern",
    title: "Null-rate spikes from upstream ETL failures",
    excerpt:
      "Symptoms, likely root causes and the exact telemetry Probe queries first.",
    reads: 131,
    updated: "2 weeks ago",
  },
  {
    id: "KB-106",
    category: "Reference",
    title: "Confidence scoring model — Probe v0.4",
    excerpt:
      "How hypothesis confidence is computed from evidence weights, temporal coincidence and prior investigations.",
    reads: 58,
    updated: "3 weeks ago",
  },
];

function KBPage() {
  const [q, setQ] = useState("");
  const rows = articles.filter(
    (a) =>
      q === "" ||
      a.title.toLowerCase().includes(q.toLowerCase()) ||
      a.excerpt.toLowerCase().includes(q.toLowerCase()),
  );

  return (
    <div className="mx-auto max-w-[1200px] px-4 py-6 md:px-8 md:py-8">
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1 className="text-[22px] font-semibold tracking-tight text-foreground">
            Knowledge base
          </h1>
          <p className="mt-1 text-[13px] text-muted-foreground">
            Playbooks, patterns and reference material Probe draws on during
            investigations.
          </p>
        </div>
      </div>

      <div className="mt-5 relative max-w-lg">
        <Search className="pointer-events-none absolute left-2.5 top-1/2 size-3.5 -translate-y-1/2 text-muted-foreground" />
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search playbooks…"
          className="h-9 w-full rounded-md border border-border bg-surface pl-8 pr-3 text-[13px] text-foreground placeholder:text-muted-foreground focus:border-primary/60 focus:outline-none focus:ring-2 focus:ring-primary/20"
        />
      </div>

      <div className="mt-6 divide-y divide-border rounded-lg border border-border bg-surface">
        {rows.map((a) => (
          <a
            key={a.id}
            href="#"
            className="group flex items-start gap-4 px-4 py-4 transition-colors hover:bg-elevated/50"
          >
            <div className="mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-md border border-border bg-background text-muted-foreground">
              <BookOpen className="size-3.5" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <span className="font-mono text-[10.5px] text-muted-foreground">
                  {a.id}
                </span>
                <span className="rounded bg-surface-2 px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
                  {a.category}
                </span>
              </div>
              <h3 className="mt-1 text-[13.5px] font-medium text-foreground group-hover:text-primary">
                {a.title}
              </h3>
              <p className="mt-1 text-[12px] text-muted-foreground line-clamp-2">
                {a.excerpt}
              </p>
              <div className="mt-2 flex items-center gap-3 text-[11px] text-muted-foreground">
                <span>{a.reads} reads</span>
                <span className="text-border-strong">·</span>
                <span>Updated {a.updated}</span>
              </div>
            </div>
            <ArrowUpRight className="mt-1 size-4 text-muted-foreground group-hover:text-foreground" />
          </a>
        ))}
      </div>
    </div>
  );
}
