export type Severity = "critical" | "high" | "medium" | "low";
export type InvestigationStatus =
  | "running"
  | "completed"
  | "failed"
  | "queued";

export type Investigation = {
  id: string;
  incident: string;
  model: string;
  modelVersion: string;
  severity: Severity;
  status: InvestigationStatus;
  startedAt: string;
  completedAt: string | null;
  durationMs: number | null;
  confidence: number;
  recommendation: string;
  assignee: string;
  environment: "production" | "staging";
  region: string;
};

export const investigations: Investigation[] = [
  {
    id: "INV-4821",
    incident: "Feature drift on user_embedding_v3",
    model: "recommendation-ranker",
    modelVersion: "v4.12.0",
    severity: "critical",
    status: "running",
    startedAt: "2026-07-28T09:14:00Z",
    completedAt: null,
    durationMs: null,
    confidence: 0.72,
    recommendation: "Roll back to v4.11.2 pending audit",
    assignee: "probe-agent",
    environment: "production",
    region: "us-east-1",
  },
  {
    id: "INV-4820",
    incident: "Latency regression on scoring endpoint",
    model: "fraud-classifier",
    modelVersion: "v2.7.3",
    severity: "high",
    status: "completed",
    startedAt: "2026-07-28T08:02:00Z",
    completedAt: "2026-07-28T08:09:34Z",
    durationMs: 454000,
    confidence: 0.94,
    recommendation: "Enable request batching (see EXP-217)",
    assignee: "probe-agent",
    environment: "production",
    region: "eu-west-1",
  },
  {
    id: "INV-4819",
    incident: "Prediction distribution shift, class 2",
    model: "churn-predictor",
    modelVersion: "v1.4.0",
    severity: "medium",
    status: "completed",
    startedAt: "2026-07-28T06:41:00Z",
    completedAt: "2026-07-28T06:46:12Z",
    durationMs: 312000,
    confidence: 0.81,
    recommendation: "Retrain with last 14d window",
    assignee: "probe-agent",
    environment: "production",
    region: "us-west-2",
  },
  {
    id: "INV-4818",
    incident: "Null rate spike in feature `session_len`",
    model: "recommendation-ranker",
    modelVersion: "v4.12.0",
    severity: "high",
    status: "completed",
    startedAt: "2026-07-28T05:22:00Z",
    completedAt: "2026-07-28T05:28:41Z",
    durationMs: 401000,
    confidence: 0.88,
    recommendation: "Patch upstream ETL job `sessions_daily`",
    assignee: "probe-agent",
    environment: "production",
    region: "us-east-1",
  },
  {
    id: "INV-4817",
    incident: "Calibration drift, ECE 0.11 → 0.19",
    model: "credit-risk-v3",
    modelVersion: "v3.2.1",
    severity: "critical",
    status: "completed",
    startedAt: "2026-07-27T22:11:00Z",
    completedAt: "2026-07-27T22:19:56Z",
    durationMs: 536000,
    confidence: 0.91,
    recommendation: "Apply Platt scaling; freeze deploys",
    assignee: "probe-agent",
    environment: "production",
    region: "eu-west-1",
  },
  {
    id: "INV-4816",
    incident: "Embedding norm collapse",
    model: "search-embed-large",
    modelVersion: "v0.9.0",
    severity: "medium",
    status: "failed",
    startedAt: "2026-07-27T20:04:00Z",
    completedAt: "2026-07-27T20:05:48Z",
    durationMs: 108000,
    confidence: 0.42,
    recommendation: "Insufficient telemetry — enable trace sampling",
    assignee: "probe-agent",
    environment: "staging",
    region: "us-east-1",
  },
  {
    id: "INV-4815",
    incident: "Throughput drop after autoscaler event",
    model: "fraud-classifier",
    modelVersion: "v2.7.3",
    severity: "low",
    status: "completed",
    startedAt: "2026-07-27T18:33:00Z",
    completedAt: "2026-07-27T18:36:11Z",
    durationMs: 191000,
    confidence: 0.77,
    recommendation: "Increase min replicas from 4 → 6",
    assignee: "probe-agent",
    environment: "production",
    region: "ap-south-1",
  },
  {
    id: "INV-4814",
    incident: "PSI 0.28 on `device_type`",
    model: "recommendation-ranker",
    modelVersion: "v4.11.2",
    severity: "medium",
    status: "queued",
    startedAt: "2026-07-28T09:20:00Z",
    completedAt: null,
    durationMs: null,
    confidence: 0,
    recommendation: "—",
    assignee: "probe-agent",
    environment: "production",
    region: "us-east-1",
  },
];

export type TimelineStep = {
  key: string;
  label: string;
  status: "done" | "running" | "queued" | "failed";
  startedAt: string;
  durationMs: number | null;
  detail?: string;
};

export const timeline: TimelineStep[] = [
  {
    key: "received",
    label: "Incident received",
    status: "done",
    startedAt: "09:14:02",
    durationMs: 40,
    detail: "DriftGuard alert alert_9f2c ingested",
  },
  {
    key: "telemetry",
    label: "Telemetry retrieved",
    status: "done",
    startedAt: "09:14:04",
    durationMs: 2100,
    detail: "48h window · 12 sources · 1.4M rows",
  },
  {
    key: "planner",
    label: "Planner complete",
    status: "done",
    startedAt: "09:14:07",
    durationMs: 1800,
    detail: "6 candidate hypotheses, 4 experiments",
  },
  {
    key: "evidence",
    label: "Evidence collected",
    status: "done",
    startedAt: "09:14:11",
    durationMs: 8400,
    detail: "9 evidence artifacts",
  },
  {
    key: "hypothesis",
    label: "Hypothesis generated",
    status: "done",
    startedAt: "09:14:22",
    durationMs: 3200,
    detail: "Top hypothesis @ 0.72 confidence",
  },
  {
    key: "eval",
    label: "Evaluation running",
    status: "running",
    startedAt: "09:14:28",
    durationMs: null,
    detail: "Backtesting on 7d holdout",
  },
  {
    key: "report",
    label: "Report generation",
    status: "queued",
    startedAt: "—",
    durationMs: null,
  },
];

export type Evidence = {
  id: string;
  title: string;
  confidence: number;
  explanation: string;
  metrics: { label: string; value: string; delta?: string; tone?: "up" | "down" | "flat" }[];
  metadata: Record<string, string | number>;
};

export const evidenceItems: Evidence[] = [
  {
    id: "EV-01",
    title: "PSI on `user_embedding_v3` breached threshold",
    confidence: 0.93,
    explanation:
      "Population stability index for user_embedding_v3 rose from 0.06 (baseline, 30d) to 0.31 in the last 6 hours. The shift concentrates in dimensions 12, 47 and 88, matching the release of upstream embedding job `embed_daily@2f7a`.",
    metrics: [
      { label: "PSI (6h)", value: "0.31", delta: "+0.25", tone: "up" },
      { label: "Baseline", value: "0.06" },
      { label: "Threshold", value: "0.20" },
      { label: "Affected dims", value: "3 / 128" },
    ],
    metadata: {
      source: "feature_store.metrics",
      window: "6h",
      job: "embed_daily@2f7a",
      commit: "2f7a91c",
    },
  },
  {
    id: "EV-02",
    title: "Upstream job `embed_daily` deployed 42m before incident",
    confidence: 0.88,
    explanation:
      "Deployment of embed_daily commit 2f7a91c completed at 08:32 UTC. Change introduced a normalization step (L2 → L1) affecting embedding scale. Correlates with the onset of drift at 09:14.",
    metrics: [
      { label: "Deploy → alert", value: "42m" },
      { label: "PR", value: "#1284" },
      { label: "Author", value: "@k.moreno" },
    ],
    metadata: {
      pipeline: "embed_daily",
      commit: "2f7a91c",
      pr: "https://git.internal/ml/embed/pull/1284",
    },
  },
  {
    id: "EV-03",
    title: "No hardware or region-level anomaly detected",
    confidence: 0.71,
    explanation:
      "Serving cluster metrics (CPU, memory, GPU util, p99 latency) remain within nominal bands. Region us-east-1 shows no infra correlation. Rules out infra as the driver.",
    metrics: [
      { label: "p99 latency", value: "84ms", delta: "-2ms", tone: "flat" },
      { label: "Error rate", value: "0.02%" },
      { label: "GPU util", value: "63%" },
    ],
    metadata: { source: "datadog", cluster: "ml-serve-use1-2" },
  },
];

export type Hypothesis = {
  id: string;
  title: string;
  confidence: number;
  supporting: string[];
  weaknesses: string[];
};

export const hypotheses: Hypothesis[] = [
  {
    id: "H-01",
    title: "Upstream embedding normalization change altered feature scale",
    confidence: 0.72,
    supporting: [
      "PSI concentrated in dims 12, 47, 88 (EV-01)",
      "embed_daily deploy 42m before alert (EV-02)",
      "L2→L1 normalization visible in PR #1284",
    ],
    weaknesses: [
      "Baseline PSI window is 30d — could mask slow shift",
      "Downstream ranker not retrained against new distribution",
    ],
  },
  {
    id: "H-02",
    title: "User cohort mix shifted (marketing campaign launch)",
    confidence: 0.31,
    supporting: [
      "Campaign `summer_promo_v2` launched at 08:45",
      "Traffic +18% vs 7d avg",
    ],
    weaknesses: [
      "PSI on `device_type` and `country` unchanged",
      "New-user ratio only +2.4pp",
    ],
  },
  {
    id: "H-03",
    title: "Model version regression (v4.12.0 rollout)",
    confidence: 0.14,
    supporting: ["v4.12.0 rolled out 4h before alert"],
    weaknesses: [
      "Canary showed no divergence for 6h prior",
      "Feature-level drift, not prediction-level",
    ],
  },
];

export type Experiment = {
  id: string;
  title: string;
  cost: string;
  improvement: string;
  risk: "low" | "medium" | "high";
  priority: "P0" | "P1" | "P2";
  description: string;
};

export const experiments: Experiment[] = [
  {
    id: "EXP-217",
    title: "Roll back `embed_daily` to commit 5c9e",
    cost: "~4 min",
    improvement: "PSI → 0.07 (est.)",
    risk: "low",
    priority: "P0",
    description:
      "Revert the L2→L1 normalization change. Ranker distribution should return to baseline within one refresh cycle.",
  },
  {
    id: "EXP-218",
    title: "Retrain ranker head on new embedding distribution",
    cost: "~2.4 GPU-hr",
    improvement: "nDCG +0.6% (est.)",
    risk: "medium",
    priority: "P1",
    description:
      "Keeps the new embedding scheme but adapts the downstream ranker. Preferable if the upstream change is intentional.",
  },
  {
    id: "EXP-219",
    title: "Tighten PSI alert threshold to 0.15 for embedding features",
    cost: "config only",
    improvement: "MTTD −38%",
    risk: "low",
    priority: "P2",
    description:
      "Would have surfaced this incident ~22 minutes earlier based on backfill.",
  },
];

export const chartSeries = [
  { t: "00:00", incidents: 2, resolved: 1 },
  { t: "02:00", incidents: 1, resolved: 2 },
  { t: "04:00", incidents: 3, resolved: 2 },
  { t: "06:00", incidents: 4, resolved: 3 },
  { t: "08:00", incidents: 6, resolved: 4 },
  { t: "10:00", incidents: 5, resolved: 5 },
  { t: "12:00", incidents: 3, resolved: 4 },
  { t: "14:00", incidents: 4, resolved: 3 },
  { t: "16:00", incidents: 2, resolved: 3 },
  { t: "18:00", incidents: 3, resolved: 2 },
  { t: "20:00", incidents: 2, resolved: 3 },
  { t: "22:00", incidents: 1, resolved: 2 },
];

export function getInvestigation(id: string) {
  return investigations.find((i) => i.id === id) ?? investigations[0];
}
