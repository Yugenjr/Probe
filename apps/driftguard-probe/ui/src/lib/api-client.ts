export interface InvestigationSummary {
  id: string;
  status: 'received' | 'planning' | 'collecting_evidence' | 'hypothesis_synthesis' | 'experimental_validation' | 'remediation_ready' | 'completed' | 'failed';
  model: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  confidence: number;
  started_at: string;
  completed_at: string | null;
}

export interface TimelineItem {
  agent: string;
  status: 'completed' | 'failed' | 'running' | 'queued';
  started_at: string;
  finished_at: string;
  duration_ms: number;
}

export interface EvidenceItem {
  evidence_id: string;
  source_provider: string;
  retrieved_by_tool: string;
  summary: string;
  confidence_weight: number;
  feature_name?: string;
  distance_algorithm?: string;
  observed_distance?: number;
  alarm_threshold?: number;
}

export interface HypothesisItem {
  hypothesis_id: string;
  title: string;
  detailed_reasoning: string;
  supporting_evidence_ids: string[];
  likelihood_score: number;
  verified_by_simulation: boolean;
  explanation?: string;
  confidence?: number;
  weaknesses?: string[];
}

export interface RecommendationItem {
  action: string;
  reason: string;
  priority: string;
  estimated_risk: string;
  estimated_time: string;
}

export interface EvaluationResultItem {
  best_hypothesis: HypothesisItem;
  alternatives: HypothesisItem[];
  recommended_actions: RecommendationItem[];
  confidence: number;
}

export interface ReportItem {
  report_id: string;
  investigation_id: string;
  primary_root_cause: string;
  markdown_content: string;
}

export interface APIResponse<T> {
  status: 'success' | 'error';
  data: T;
  message?: string;
}

const API_BASE = "http://localhost:8002/api/v1";

export async function fetchInvestigations(): Promise<InvestigationSummary[]> {
  const res = await fetch(`${API_BASE}/investigations`);
  if (!res.ok) throw new Error("Backend unavailable");
  const json: APIResponse<{ items: InvestigationSummary[] }> = await res.json();
  return json.data.items;
}

export async function fetchInvestigationDetails(id: string): Promise<any> {
  const res = await fetch(`${API_BASE}/investigations/${id}`);
  if (!res.ok) throw new Error("Backend unavailable");
  const json: APIResponse<any> = await res.json();
  return json.data;
}

export async function fetchTimeline(id: string): Promise<TimelineItem[]> {
  const res = await fetch(`${API_BASE}/investigations/${id}/timeline`);
  if (!res.ok) throw new Error("Backend unavailable");
  const json: APIResponse<{ timeline: TimelineItem[] }> = await res.json();
  return json.data.timeline;
}

export async function fetchEvidence(id: string): Promise<{ universal_evidence: EvidenceItem[], legacy_evidence: any[] }> {
  const res = await fetch(`${API_BASE}/investigations/${id}/evidence`);
  if (!res.ok) throw new Error("Backend unavailable");
  const json: APIResponse<{ universal_evidence: EvidenceItem[], legacy_evidence: any[] }> = await res.json();
  return json.data;
}

export async function fetchHypotheses(id: string): Promise<HypothesisItem[]> {
  const res = await fetch(`${API_BASE}/investigations/${id}/hypotheses`);
  if (!res.ok) throw new Error("Backend unavailable");
  const json: APIResponse<{ hypotheses: HypothesisItem[] }> = await res.json();
  return json.data.hypotheses;
}

export async function fetchEvaluation(id: string): Promise<EvaluationResultItem | null> {
  const res = await fetch(`${API_BASE}/investigations/${id}/evaluation`);
  if (!res.ok) throw new Error("Backend unavailable");
  const json: APIResponse<{ evaluation_result: EvaluationResultItem | null }> = await res.json();
  return json.data.evaluation_result;
}

export async function fetchReport(id: string): Promise<ReportItem | null> {
  const res = await fetch(`${API_BASE}/investigations/${id}/report`);
  if (!res.ok) throw new Error("Backend unavailable");
  const json: APIResponse<{ report: ReportItem | null }> = await res.json();
  return json.data.report;
}
