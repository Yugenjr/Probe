import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  fetchInvestigations,
  fetchTimeline,
  fetchEvidence,
  fetchHypotheses,
  fetchEvaluation,
  fetchReport
} from "./api-client";

global.fetch = vi.fn();

describe("api-client frontend integration", () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it("should fetch all investigation summaries", async () => {
    const mockResponse = {
      status: "success",
      data: {
        items: [
          {
            id: "inv-01",
            status: "completed",
            model: "recommendation-ranker",
            severity: "critical",
            confidence: 0.94,
            started_at: "2026-07-28T09:14:00Z",
            completed_at: "2026-07-28T09:18:00Z"
          }
        ]
      }
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse
    });

    const data = await fetchInvestigations();
    expect(data).toHaveLength(1);
    expect(data[0].id).toBe("inv-01");
    expect(data[0].model).toBe("recommendation-ranker");
  });

  it("should retrieve timeline steps for a session", async () => {
    const mockTimeline = {
      status: "success",
      data: {
        timeline: [
          {
            agent: "Planner",
            status: "completed",
            started_at: "2026-07-28T09:14:00Z",
            finished_at: "2026-07-28T09:14:02Z",
            duration_ms: 2000
          }
        ]
      }
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockTimeline
    });

    const timeline = await fetchTimeline("inv-01");
    expect(timeline).toHaveLength(1);
    expect(timeline[0].agent).toBe("Planner");
    expect(timeline[0].duration_ms).toBe(2000);
  });

  it("should retrieve evidence blocks", async () => {
    const mockEvidence = {
      status: "success",
      data: {
        universal_evidence: [
          {
            evidence_id: "ev-01",
            source_provider: "Evidently",
            retrieved_by_tool: "DriftExtractor",
            summary: "Drift detected on age",
            confidence_weight: 0.9
          }
        ],
        legacy_evidence: []
      }
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockEvidence
    });

    const evidence = await fetchEvidence("inv-01");
    expect(evidence.universal_evidence).toHaveLength(1);
    expect(evidence.universal_evidence[0].evidence_id).toBe("ev-01");
  });

  it("should retrieve hypotheses syntheses", async () => {
    const mockHypotheses = {
      status: "success",
      data: {
        hypotheses: [
          {
            hypothesis_id: "hyp-01",
            title: "Wasserstein shift",
            detailed_reasoning: "Wasserstein drift detected.",
            supporting_evidence_ids: ["ev-01"],
            likelihood_score: 0.92,
            verified_by_simulation: false
          }
        ]
      }
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockHypotheses
    });

    const list = await fetchHypotheses("inv-01");
    expect(list).toHaveLength(1);
    expect(list[0].hypothesis_id).toBe("hyp-01");
  });

  it("should retrieve evaluator actions", async () => {
    const mockEvaluation = {
      status: "success",
      data: {
        evaluation_result: {
          best_hypothesis: null,
          alternatives: [],
          recommended_actions: [
            {
              action: "Rollback",
              reason: "Preprocessing change in commit.",
              priority: "P0",
              estimated_risk: "Low",
              estimated_time: "5 min"
            }
          ],
          confidence: 0.92
        }
      }
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockEvaluation
    });

    const result = await fetchEvaluation("inv-01");
    expect(result).not.toBeNull();
    expect(result!.recommended_actions).toHaveLength(1);
    expect(result!.recommended_actions[0].action).toBe("Rollback");
  });

  it("should fetch executive reports", async () => {
    const mockReport = {
      status: "success",
      data: {
        report: {
          report_id: "rep-01",
          investigation_id: "inv-01",
          primary_root_cause: "Wasserstein shift",
          markdown_content: "# Report"
        }
      }
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockReport
    });

    const report = await fetchReport("inv-01");
    expect(report).not.toBeNull();
    expect(report!.report_id).toBe("rep-01");
  });
});
