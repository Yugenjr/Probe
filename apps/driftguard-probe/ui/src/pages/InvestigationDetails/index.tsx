import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import ReactFlow, { Background, Controls, Edge, Node } from "reactflow";
import "reactflow/dist/style.css";
import { EvidenceNodeComponent } from "../../components/graphs/EvidenceNodeComponent";
import {
  CheckCircle2,
  AlertTriangle,
  Clock,
  ShieldCheck,
  Terminal,
  FileText,
  Activity,
  Layers,
  Check,
  X,
  ChevronDown,
  ArrowUpRight,
} from "lucide-react";

const nodeTypes = { evidenceNode: EvidenceNodeComponent };

export const InvestigationDetails: React.FC = () => {
  const { sessionId = "inc-prod-sagemaker-9001" } = useParams();
  const [activeTab, setActiveTab] = useState<"reasoning" | "evidence" | "graph" | "timeline" | "raw">("reasoning");
  const [actionStatus, setActionStatus] = useState<"pending" | "approved" | "rejected">("pending");

  // Simulated AI reasoning steps for generative progressive disclosure
  const [stepIndex, setStepIndex] = useState(0);
  const reasoningSteps = [
    { text: "Collecting telemetry stream anomalies from primary webhook endpoints", done: stepIndex >= 1 },
    { text: "Querying DriftGuard enterprise governance database (18 model lineages scanned)", done: stepIndex >= 2 },
    { text: "Querying WhyLabs statistical feature profiles (Covariate age distribution shift confirmed)", done: stepIndex >= 3 },
    { text: "Searching previous incidents and vector runbook guides (1 exact lineage match found)", done: stepIndex >= 4 },
    { text: "Building topological causal Evidence Graph & calculating Bayesian verifications...", done: stepIndex >= 5 },
    { text: "Executing empirical simulation replay stress tests (Falsification p=0.004 passed)", done: stepIndex >= 6 },
    { text: "Recommendation generated: Engineering Change Request ready for SRE authorization.", done: stepIndex >= 6 },
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setStepIndex((prev) => (prev < 6 ? prev + 1 : prev));
    }, 1200);
    return () => clearInterval(timer);
  }, []);

  // React Flow Evidence Graph node structures
  const initialNodes: Node[] = [
    {
      id: "node-drift",
      type: "evidenceNode",
      position: { x: 40, y: 60 },
      data: { evidence_type: "feature_drift", summary: "Wasserstein Covariate Age Shift (W: 0.28)", empirical_weight: 0.9, source_provider: "WhyLabs", node_id: "hash-d001" },
    },
    {
      id: "node-lat",
      type: "evidenceNode",
      position: { x: 380, y: 60 },
      data: { evidence_type: "latency_curve", summary: "P99 Inference Latency Surging (&gt;450ms)", empirical_weight: 0.85, source_provider: "OpenTelemetry", node_id: "hash-l002" },
    },
    {
      id: "node-rb",
      type: "evidenceNode",
      position: { x: 210, y: 240 },
      data: { evidence_type: "runbook_guidance", summary: "Runbook Pattern #42: Covariate Slice Retrain", empirical_weight: 0.92, source_provider: "Knowledge DB", node_id: "hash-r003" },
    },
  ];

  const initialEdges: Edge[] = [
    { id: "edge-1", source: "node-drift", target: "node-lat", label: "CAUSAL_TO (W: 0.88)", animated: true, style: { stroke: "#3b82f6", strokeWidth: 2 } },
    { id: "edge-2", source: "node-rb", target: "node-lat", label: "SUPPORTED_BY", style: { stroke: "#10b981", strokeDasharray: "4 4", strokeWidth: 1.5 } },
  ];

  return (
    <div className="flex h-full w-full bg-background font-sans overflow-hidden">
      {/* CENTRAL MAIN WORKSPACE (Fluid Area) */}
      <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden border-r border-border">
        {/* Workspace Top Header Bar */}
        <div className="px-6 py-4 border-b border-border bg-card/50 flex items-center justify-between shrink-0">
          <div className="space-y-1">
            <div className="flex items-center space-x-3">
              <span className="text-sm font-bold font-mono text-slate-100">{sessionId}: Fraud Detection Pipeline</span>
              <span className="px-2 py-0.5 rounded text-[10px] bg-blue-950 text-blue-300 border border-blue-800 font-mono uppercase font-bold">
                Status: {stepIndex >= 6 ? "Recommendation Ready" : "Investigating..."}
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] bg-red-950 text-red-300 border border-red-800 font-mono uppercase font-bold">
                Critical Severity
              </span>
            </div>
          </div>
          <div className="flex items-center space-x-4 text-xs font-mono text-slate-400">
            <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> Started 2 minutes ago</span>
          </div>
        </div>

        {/* Diagnostic Tab Bar (Reasoning / Evidence / Graph / Timeline / Raw Data) */}
        <div className="flex items-center px-6 border-b border-border bg-slate-950/80 text-xs font-semibold space-x-6 shrink-0 select-none">
          {[
            { id: "reasoning", label: "Reasoning Stream" },
            { id: "evidence", label: "Evidence Items (3)" },
            { id: "graph", label: "Evidence Graph" },
            { id: "timeline", label: "Timeline & Confidence Loops" },
            { id: "raw", label: "Raw CQRS Payloads" },
          ].map((t) => (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id as any)}
              className={`py-3 relative transition-colors ${
                activeTab === t.id ? "text-blue-400 font-bold" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {t.label}
              {activeTab === t.id && <span className="absolute bottom-0 left-0 w-full h-0.5 bg-blue-500" />}
            </button>
          ))}
        </div>

        {/* Tab View Surfaces */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-950/20">
          {/* TAB 1: REASONING STREAM & HYPOTHESES */}
          {activeTab === "reasoning" && (
            <div className="space-y-6 max-w-4xl">
              {/* Progressive AI Reasoning Stream */}
              <div className="bg-card border border-border rounded-md p-5 space-y-4 shadow-sm">
                <div className="flex items-center justify-between border-b border-slate-900 pb-3 font-mono text-xs text-slate-400">
                  <span className="flex items-center gap-2 text-slate-200 font-semibold">
                    <Terminal className="w-4 h-4 text-blue-400" /> Probe Autonomous Diagnostic Engine
                  </span>
                  <span className="text-blue-400 font-medium animate-pulse">
                    {stepIndex < 6 ? "Executing reasoning loop..." : "Investigation stabilized"}
                  </span>
                </div>

                <div className="space-y-2.5 font-mono text-xs">
                  {reasoningSteps.map((step, idx) => (
                    <div
                      key={idx}
                      className={`flex items-start space-x-2.5 transition-opacity duration-300 ${
                        idx <= stepIndex ? "opacity-100" : "opacity-30"
                      }`}
                    >
                      <span className="shrink-0 pt-0.5">
                        {step.done ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                        ) : idx === stepIndex ? (
                          <span className="w-3 h-3 block border-2 border-blue-400 border-t-transparent rounded-full animate-spin ml-0.5" />
                        ) : (
                          <span className="w-3 h-3 block border border-slate-700 rounded-full ml-0.5" />
                        )}
                      </span>
                      <span className={step.done ? "text-slate-300" : "text-slate-500"}>{step.text}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Competing Causal Hypotheses Cards */}
              {stepIndex >= 3 && (
                <div className="space-y-3 pt-2">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">
                    Dominant Verified Hypothesis
                  </h3>
                  <div className="bg-slate-900/90 border border-slate-700 rounded-md p-5 space-y-4 shadow-md">
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <span className="text-sm font-bold text-slate-100 flex items-center gap-2">
                          <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
                          Covariate Demographic Distribution Shift Inducing Vector Cache Miss
                        </span>
                        <p className="text-xs text-slate-400 font-normal leading-relaxed pt-1">
                          Mathematical Evidence Graph correlation confirmed that demographic feature distribution drift immediately following deployment v18 triggered embedding lookup bottlenecks during inference, causing P99 latency surges without infrastructure outages.
                        </p>
                      </div>
                      <div className="text-right shrink-0 ml-6 font-mono">
                        <div className="text-xl font-extrabold text-emerald-400">93%</div>
                        <div className="text-[10px] text-slate-400">Bayesian Confidence</div>
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-3 pt-3 border-t border-slate-800 text-xs font-mono">
                      <div className="bg-slate-950 p-2.5 rounded border border-slate-900">
                        <div className="text-[10px] text-slate-500">Supporting Evidence</div>
                        <div className="text-slate-200 font-bold mt-0.5">3 Verified Items</div>
                      </div>
                      <div className="bg-slate-950 p-2.5 rounded border border-slate-900">
                        <div className="text-[10px] text-slate-500">Contradicting Evidence</div>
                        <div className="text-slate-200 font-bold mt-0.5">0 Contradictions</div>
                      </div>
                      <div className="bg-slate-950 p-2.5 rounded border border-slate-900">
                        <div className="text-[10px] text-slate-500">Empirical Simulation</div>
                        <div className="text-emerald-400 font-bold mt-0.5">Passed (p=0.004)</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Engineering Change Request Recommendation (PR Review Studio) */}
              {stepIndex >= 6 && (
                <div className="space-y-3 pt-4">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono flex items-center justify-between">
                    <span>Actionable Engineering Recommendation</span>
                    <span className="text-amber-400">Required Sign-off: SRE Lead</span>
                  </h3>

                  <div className="bg-card border-2 border-blue-900/60 rounded-md overflow-hidden shadow-lg">
                    <div className="px-5 py-3.5 bg-slate-900/80 border-b border-slate-800 flex items-center justify-between">
                      <span className="font-bold text-sm text-slate-100 font-mono">
                        CHANGE REQUEST: Rollback preprocessing pipeline &amp; dispatch SageMaker retraining
                      </span>
                      <span className="text-xs font-bold font-mono text-emerald-400 bg-emerald-950/60 border border-emerald-800/80 px-2 py-0.5 rounded">
                        Expected Recovery: +12%
                      </span>
                    </div>

                    <div className="p-5 space-y-4 text-xs font-mono">
                      <div className="space-y-2 text-slate-300 font-sans">
                        <p className="leading-relaxed">
                          Rollback online feature extraction pipeline from version v18 to v17, apply dynamic 7-day demographic feature slice filtering, and trigger automated shadow model re-calibration.
                        </p>
                      </div>

                      <div className="grid grid-cols-3 gap-4 py-2 border-y border-slate-900 text-slate-400">
                        <div>
                          <span className="text-[10px] block text-slate-500">RISK PROFILE</span>
                          <span className="text-emerald-400 font-semibold font-mono">Low (Canary Deployment)</span>
                        </div>
                        <div>
                          <span className="text-[10px] block text-slate-500">ESTIMATED COMPUTE COST</span>
                          <span className="text-slate-200 font-semibold font-mono">$4.20 / compute hour</span>
                        </div>
                        <div>
                          <span className="text-[10px] block text-slate-500">REQUIRED INTERLOCK</span>
                          <span className="text-amber-400 font-semibold font-mono">Tier-1 SRE Authorization</span>
                        </div>
                      </div>

                      {/* Action Buttons */}
                      <div className="pt-2 flex items-center justify-between font-sans">
                        <div className="flex items-center space-x-3">
                          {actionStatus === "pending" ? (
                            <>
                              <button
                                onClick={() => setActionStatus("approved")}
                                className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded shadow-md transition-all duration-150 flex items-center gap-2 text-xs"
                              >
                                <Check className="w-4 h-4" /> Approve &amp; Execute Change
                              </button>
                              <button
                                onClick={() => setActionStatus("rejected")}
                                className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 font-semibold rounded transition-all duration-150 text-xs"
                              >
                                Reject
                              </button>
                            </>
                          ) : actionStatus === "approved" ? (
                            <div className="px-5 py-2 bg-emerald-950 border border-emerald-700 text-emerald-300 font-bold rounded flex items-center gap-2 text-xs font-mono">
                              <CheckCircle2 className="w-4 h-4" /> Change Request Approved &amp; Pipeline Dispatched
                            </div>
                          ) : (
                            <div className="px-5 py-2 bg-red-950 border border-red-800 text-red-300 font-bold rounded flex items-center gap-2 text-xs font-mono">
                              <X className="w-4 h-4" /> Change Request Rejected
                            </div>
                          )}
                        </div>
                        <button
                          onClick={() => setActiveTab("evidence")}
                          className="text-slate-400 hover:text-slate-200 text-xs font-mono underline"
                        >
                          Inspect Corroborating Evidence &rarr;
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: EVIDENCE (First-Class Domain Concepts) */}
          {activeTab === "evidence" && (
            <div className="space-y-4 max-w-4xl font-mono text-xs">
              <div className="flex items-center justify-between font-sans">
                <div>
                  <h3 className="text-sm font-bold text-slate-100">Verified Evidence Registry</h3>
                  <p className="text-xs text-slate-400">First-class empirical items gathered across multi-platform integrations.</p>
                </div>
              </div>

              <div className="space-y-3">
                {[
                  { title: "Feature Drift Detection: Covariate Age Distribution", provider: "WhyLabs Telemetry", timestamp: "14:01:22 UTC", weight: 0.90, desc: "Observed Wasserstein metric distance 0.28 exceeding allowed threshold (0.10). P-value: 0.001." },
                  { title: "P99 Inference Latency Degradation Curve", provider: "OpenTelemetry Traces", timestamp: "14:01:25 UTC", weight: 0.85, desc: "Online lookup latency surged to 480ms aligning precisely with covariate schema shift window." },
                  { title: "Operational Runbook Lineage Verification (#42)", provider: "Internal Knowledge Vector DB", timestamp: "14:01:28 UTC", weight: 0.92, desc: "Historical incident signature match confirming preprocessing rollback mitigates vector lookup stall." },
                ].map((ev, idx) => (
                  <div key={idx} className="bg-card border border-border rounded-md p-4 space-y-2 hover:border-slate-600 transition-colors">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-blue-400 text-sm">{ev.title}</span>
                      <span className="text-[11px] px-2 py-0.5 bg-slate-900 border border-slate-700 rounded text-slate-300">
                        Weight: {ev.weight}
                      </span>
                    </div>
                    <p className="text-slate-300 font-sans text-xs">{ev.desc}</p>
                    <div className="pt-2 border-t border-slate-900 flex justify-between text-[11px] text-slate-500">
                      <span>Source Platform: {ev.provider}</span>
                      <span>Ingestion: {ev.timestamp}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: EVIDENCE GRAPH (Dedicated Topological View) */}
          {activeTab === "graph" && (
            <div className="flex flex-col h-[520px] w-full border border-border rounded-md overflow-hidden bg-slate-950/60 shadow-inner">
              <div className="p-3 border-b border-border bg-card/60 flex items-center justify-between text-xs font-mono">
                <span className="text-slate-200 font-semibold flex items-center gap-2">
                  <Layers className="w-4 h-4 text-blue-400" /> Causal Topological Evidence Graph
                </span>
                <span className="text-slate-400">3 Domain Nodes | 2 Directed Relationships</span>
              </div>
              <div className="flex-1 relative">
                <ReactFlow nodes={initialNodes} edges={initialEdges} nodeTypes={nodeTypes} fitView>
                  <Background gap={16} size={1} color="#1e293b" />
                  <Controls className="bg-slate-900 border border-slate-700 fill-slate-300" />
                </ReactFlow>
              </div>
            </div>
          )}

          {/* TAB 4: TIMELINE (Live Confidence Escalation Loops) */}
          {activeTab === "timeline" && (
            <div className="space-y-6 max-w-3xl font-mono text-xs">
              <div>
                <h3 className="font-sans text-sm font-bold text-slate-100">Live Investigation Timeline &amp; Confidence Escalation</h3>
                <p className="font-sans text-xs text-slate-400 mt-0.5">Chronological record of autonomous agent hypothesis verifications and feedback refinement cycles.</p>
              </div>

              <div className="border-l-2 border-blue-600 pl-6 space-y-6 relative ml-2">
                <div className="space-y-1">
                  <span className="text-[11px] text-slate-400">14:01:22 UTC</span>
                  <div className="font-bold text-slate-200">Telemetry Ingested</div>
                  <p className="text-slate-400 font-sans">Anomaly payload received via HTTP 202 webhook buffer from WhyLabs monitoring integration.</p>
                  <div className="text-blue-400 text-[11px]">Initial Bayesian Confidence: 42%</div>
                </div>

                <div className="space-y-1">
                  <span className="text-[11px] text-slate-400">14:02:04 UTC</span>
                  <div className="font-bold text-slate-200">Evidence Graph Built &amp; Correlated</div>
                  <p className="text-slate-400 font-sans">Correlated statistical demographic covariate shift with OpenTelemetry latency surge traces.</p>
                  <div className="text-emerald-400 font-bold text-[11px]">Confidence Escalated: 42% &rarr; 71%</div>
                </div>

                <div className="space-y-1">
                  <span className="text-[11px] text-slate-400">14:03:12 UTC</span>
                  <div className="font-bold text-slate-200">Empirical Simulation Stress Test Verified</div>
                  <p className="text-slate-400 font-sans">Adversarial red-team replay simulations confirmed covariate memory cache bottleneck reproduction (p=0.004).</p>
                  <div className="text-emerald-400 font-extrabold text-sm">Confidence Escalated: 71% &rarr; 93%</div>
                </div>

                <div className="space-y-1">
                  <span className="text-[11px] text-slate-400">14:03:30 UTC</span>
                  <div className="font-bold text-blue-400">Engineering Recommendation Ready</div>
                  <p className="text-slate-300 font-sans">Formulated actionable change request for SRE executive authorization.</p>
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: RAW DATA */}
          {activeTab === "raw" && (
            <div className="space-y-3 max-w-4xl font-mono text-xs">
              <div className="flex items-center justify-between font-sans">
                <span className="font-bold text-sm text-slate-100">EventSourced CQRS Journal Dump</span>
                <span className="text-xs font-mono text-slate-500">SHA256 Cryptographic Audit Log</span>
              </div>
              <pre className="bg-slate-950 border border-border p-4 rounded-md overflow-x-auto text-slate-300 leading-relaxed text-[11px]">
{JSON.stringify({
  session_id: sessionId,
  status: "RECOMMENDATION_READY",
  verified_confidence: 0.93,
  event_sequence_count: 6,
  evidence_nodes: ["hash-d001", "hash-l002", "hash-r003"],
  proposed_action: {
    intervention: "ROLLBACK_AND_RETRAIN",
    impact_recovery_percent: 12.0,
    cost_estimate_usd_hr: 4.20,
  },
}, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>

      {/* RIGHT CONTEXT PANEL (Fixed Environmental Context) */}
      <aside className="w-80 bg-card border-l border-border p-5 overflow-y-auto space-y-6 shrink-0 text-xs font-mono select-none">
        {/* Confidence Gauge */}
        <div className="space-y-2">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
            Overall Confidence
          </span>
          <div className="p-3.5 bg-slate-900 border border-slate-800 rounded-md space-y-2">
            <div className="flex items-center justify-between font-bold text-sm">
              <span className="text-emerald-400">93% Verified</span>
              <span className="text-xs text-slate-400 font-normal">Threshold: 80%</span>
            </div>
            <div className="w-full h-2 bg-slate-800 rounded overflow-hidden">
              <div className="bg-emerald-500 h-full w-[93%]" />
            </div>
            <div className="text-[10px] text-slate-400 pt-1 flex justify-between">
              <span>Empirical: +0.93</span>
              <span>Contradictions: -0.00</span>
            </div>
          </div>
        </div>

        {/* Evidence Sources (Multi-Platform Integration Checklist) */}
        <div className="space-y-2.5">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
            Integrated Evidence Sources
          </span>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-md p-3 space-y-2 font-sans">
            {[
              { name: "DriftGuard Governance", active: true },
              { name: "WhyLabs Observability", active: true },
              { name: "Evidently AI Monitors", active: true },
              { name: "Internal Runbooks DB", active: true },
              { name: "Git Commit History", active: true },
            ].map((src, idx) => (
              <div key={idx} className="flex items-center space-x-2 text-xs text-slate-300 font-medium">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>{src.name}</span>
              </div>
            ))}
          </div>
          <p className="text-[10px] text-slate-500 pt-1 font-sans">
            Probe synthetically combined diagnostic evidence across all five independent platform providers.
          </p>
        </div>

        {/* Related Incidents Lineage */}
        <div className="space-y-2">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
            Related Incidents
          </span>
          <div className="space-y-1.5 font-mono">
            <Link to="/investigations/inc-fraud-detector-v2" className="block p-2 bg-slate-900 hover:bg-slate-800/80 border border-slate-800 rounded text-blue-400 hover:underline text-[11px]">
              &bull; inc-fraud-detector-v2 (Covariate)
            </Link>
            <Link to="/investigations/inc-checkout-latency-104" className="block p-2 bg-slate-900 hover:bg-slate-800/80 border border-slate-800 rounded text-blue-400 hover:underline text-[11px]">
              &bull; inc-checkout-latency-104 (P99 Latency)
            </Link>
          </div>
        </div>

        {/* Investigation Metadata */}
        <div className="space-y-2 pt-2 border-t border-border">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
            Investigation Metadata
          </span>
          <div className="space-y-1 text-[11px] text-slate-400 font-mono">
            <div className="flex justify-between">
              <span>Execution Engine:</span>
              <span className="text-slate-200">DCG Cyclic v3.0</span>
            </div>
            <div className="flex justify-between">
              <span>Sandbox Isolation:</span>
              <span className="text-emerald-400">Wasm IPC / gRPC</span>
            </div>
            <div className="flex justify-between">
              <span>Assigned Lead:</span>
              <span className="text-slate-200">SRE Tier-1</span>
            </div>
          </div>
        </div>
      </aside>
    </div>
  );
};
