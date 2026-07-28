export type Severity = "critical" | "high" | "medium" | "low";
export type Status = "active" | "decided" | "resolved";

export interface InvestigationSummary {
  id: string;
  title: string;
  severity: Severity;
  status: Status;
  updated: string;
  pinned?: boolean;
}

export const investigations: InvestigationSummary[] = [
  { id: "INC-2043", title: "Payments Gateway Outage", severity: "critical", status: "active", updated: "2m", pinned: true },
  { id: "INC-2011", title: "Auth 5xx spike", severity: "high", status: "active", updated: "3h", pinned: true },
  { id: "INC-2044", title: "Checkout latency", severity: "high", status: "active", updated: "1m" },
  { id: "INC-2042", title: "Kafka rebalance loop", severity: "medium", status: "active", updated: "12m" },
  { id: "INC-2039", title: "DNS flap us-east-1", severity: "medium", status: "resolved", updated: "yes" },
  { id: "INC-2038", title: "Redis OOM cache-01", severity: "high", status: "resolved", updated: "yes" },
  { id: "INC-2035", title: "TLS renewal edge", severity: "low", status: "resolved", updated: "Wed" },
  { id: "INC-2031", title: "S3 signed URL 403s", severity: "medium", status: "decided", updated: "Aug 4" },
];

export const evidence = [
  { source: "cloudwatch", label: "payments-api error rate 14:41–14:48", confidence: 0.94, time: "14:41" },
  { source: "github", label: "abc12f · bump connection pool 20 → 8", confidence: 0.88, time: "14:32" },
  { source: "grafana", label: "db.latency.p99 spike +840ms", confidence: 0.91, time: "14:43" },
  { source: "pagerduty", label: "P1 · payments-api high error rate", confidence: 0.99, time: "14:44" },
  { source: "slack", label: "#payments-oncall — customer reports", confidence: 0.62, time: "14:46" },
  { source: "kubernetes", label: "payments-api rollout replicaset abc12f", confidence: 0.83, time: "14:31" },
];

export const timeline = [
  { t: "14:32:11", src: "github", text: "Merge abc12f — bump connection pool 20 → 8" },
  { t: "14:38:04", src: "argocd", text: "payments-api rollout started" },
  { t: "14:41:22", src: "cloudwatch", text: "Error rate 0.4% → 6.1%" },
  { t: "14:43:07", src: "grafana", text: "db.latency.p99 spike +840ms" },
  { t: "14:44:00", src: "pagerduty", text: "P1 alert fired · payments-api" },
  { t: "14:45:12", src: "pagerduty", text: "Acknowledged by @maya" },
  { t: "14:47:30", src: "decisionverse", text: "Investigation started · evidence collection" },
  { t: "14:48:41", src: "decisionverse", text: "Hypothesis updated · deployment 54% → 72%" },
];

export const metrics = [
  { label: "error rate", value: "6.1%", delta: "+5.7%", trend: "up" as const, spark: [1,1,2,2,1,2,3,8,14,18,16,15] },
  { label: "p99 latency", value: "1.24s", delta: "+840ms", trend: "up" as const, spark: [3,3,4,3,4,4,5,7,12,14,13,12] },
  { label: "req/s", value: "412", delta: "-38%", trend: "down" as const, spark: [12,12,13,12,11,10,9,8,7,7,6,6] },
  { label: "db conns", value: "8/8", delta: "saturated", trend: "up" as const, spark: [3,3,3,4,4,5,6,7,8,8,8,8] },
];

export const reasoning = [
  {
    obs: "Error rate rose from 0.4% to 6.1% at 14:41, ~3 minutes after payments-api rollout abc12f.",
    ev: ["cloudwatch:payments-api", "argocd:rollout"],
    inf: "Deployment is temporally correlated with degradation.",
    conf: 0.86,
  },
  {
    obs: "abc12f reduces DB connection pool from 20 to 8 per pod across 12 replicas.",
    ev: ["github:abc12f", "kubernetes:payments-api"],
    inf: "Aggregate pool capacity dropped from 240 to 96 — below observed peak (~180).",
    conf: 0.78,
  },
  {
    obs: "db.latency.p99 spikes and db.active_connections plateaus at 96.",
    ev: ["grafana:db.latency", "grafana:db.conns"],
    inf: "Connection pool exhaustion is the proximate cause of latency and 5xx.",
    conf: 0.82,
  },
];

export const hypotheses = [
  { title: "Deployment abc12f exhausted DB connection pool", confidence: 0.72, supporting: 4, refuting: 0 },
  { title: "Connection pool config drift across replicas", confidence: 0.54, supporting: 2, refuting: 1 },
  { title: "Database upgrade migration held long locks", confidence: 0.18, supporting: 1, refuting: 3 },
  { title: "Upstream provider (Stripe) degradation", confidence: 0.09, supporting: 0, refuting: 2 },
];

export const actions = [
  { text: "Rollback payments-api to prior revision", target: "argocd", requires: null as string | null },
  { text: "Restore connection pool to 20 in config", target: "github", requires: null },
  { text: "Scale replicas 12 → 18 to absorb traffic", target: "kubernetes", requires: "Kubernetes" },
  { text: "Verify p99 latency returns below 200ms", target: "grafana", requires: null },
  { text: "Post incident update to #status", target: "slack", requires: "Slack" },
];

export const session = [
  {
    who: "you" as const,
    time: "14:47",
    text: "investigate this incident",
  },
  {
    who: "ai" as const,
    time: "14:47",
    text: "Collecting logs from cloudwatch, github, grafana",
    tasks: [
      { label: "cloudwatch · 1,204 lines", state: "done" as const, dur: "0.4s" },
      { label: "github · 12 commits", state: "done" as const, dur: "0.2s" },
      { label: "grafana · streaming…", state: "running" as const, dur: "1.8s" },
    ],
  },
  {
    who: "ai" as const,
    time: "14:48",
    text: "Reading deployment abc12f",
    tasks: [
      { label: "diff analysed", state: "done" as const, dur: "0.3s" },
      { label: "correlates with latency spike (0.91)", state: "done" as const, dur: "" },
    ],
  },
  {
    who: "ai" as const,
    time: "14:48",
    text: "Hypothesis updated · Deployment caused outage  54% → 72%",
    tasks: [],
  },
];
