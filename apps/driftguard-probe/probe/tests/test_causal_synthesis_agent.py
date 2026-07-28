import unittest
import json
from probe.investigation.service import InvestigationService
from probe.providers.adapters.driftguard import DriftGuardAdapter
from probe.context.builder import ContextBuilder
from probe.evidence.extractor import EvidenceExtractor
from probe.storage.repository import InMemoryEvidenceStore
from probe.graph.builder import EvidenceGraphBuilder
from probe.reasoning.synthesis import (
    CausalSynthesisAgent, ReasoningPlanner, ReasoningStrategy,
    SynthesisOutputParser, MalformedOutputError, UnsupportedEvidenceError
)

class TestCausalSynthesisAgentV1(unittest.TestCase):
    def setUp(self):
        self.inv_service = InvestigationService()
        self.inv_id = self.inv_service.create_investigation(target_resource_id="fraud-v2")
        self.adapter = DriftGuardAdapter()
        self.ctx_builder = ContextBuilder(self.adapter)
        self.context = self.ctx_builder.build_context(investigation_id=self.inv_id, target_model_id="fraud-v2")
        
        self.extractor = EvidenceExtractor()
        self.evidence_list = self.extractor.extract_all_evidence(self.context)
        self.store = InMemoryEvidenceStore()
        for ev in self.evidence_list:
            self.store.append(ev)
            
        self.graph_builder = EvidenceGraphBuilder(self.store)
        self.topology = self.graph_builder.build_graph(investigation_id=self.inv_id)

    def test_golden_path_causal_synthesis_execution(self):
        print("=== Test 1: Golden Path Causal Synthesis (Multi-Modal / Distribution Strategy) ===")
        agent = CausalSynthesisAgent()
        hypotheses = agent.investigate(context=self.context, repository=self.store, topology=self.topology)
        
        print(f"Generated {len(hypotheses)} competing HypothesisArtifacts.")
        self.assertGreaterEqual(len(hypotheses), 2, "Must generate multiple competing explanations!")
        
        top_hypo = hypotheses[0]
        print(f"Dominant Ranked Hypothesis: '{top_hypo.root_cause_title}' | Plausibility: {top_hypo.initial_confidence}")
        print(f"Supporting Evidence IDs ({len(top_hypo.supporting_evidence_ids)}): {top_hypo.supporting_evidence_ids}")
        print("Reasoning Trace:", top_hypo.reasoning_trace)
        
        self.assertGreater(len(top_hypo.supporting_evidence_ids), 0)
        self.assertNotEqual(top_hypo.uncertainty, "INSUFFICIENT_EVIDENCE")
        self.assertEqual(top_hypo.producer_agent, "CausalSynthesisAgent-v1")
        print("[APPROVED] Golden path synthesis executed cleanly with multiple ranked hypotheses!")

    def test_reasoning_planner_strategy_selection(self):
        print("\n=== Test 2: Verify Architectural Improvement (Reasoning Planner Strategy Selection) ===")
        plan = ReasoningPlanner.create_plan(
            investigation_id=self.inv_id,
            context=self.context,
            topology=self.topology,
            repository=self.store
        )
        print(f"Selected Strategy: {plan.strategy.value}")
        print(f"Plan Rationale: {plan.rationale}")
        print(f"Primary Focus Metrics: {plan.focus_metrics}")
        self.assertIn(plan.strategy, (ReasoningStrategy.MULTI_MODAL_CORRELATION, ReasoningStrategy.DISTRIBUTION_REASONING, ReasoningStrategy.VALIDATION_REASONING))

    def test_edge_case_no_evidence_or_empty_graph(self):
        print("\n=== Test 3: Edge Case Verification (No Evidence / Empty Graph) ===")
        empty_store = InMemoryEvidenceStore()
        empty_topology = EvidenceGraphBuilder(empty_store).build_graph("inv-empty-001")
        
        agent = CausalSynthesisAgent()
        hypotheses = agent.investigate(context=self.context, repository=empty_store, topology=empty_topology)
        self.assertEqual(len(hypotheses), 1)
        ins = hypotheses[0]
        print(f"Empty Graph Output: '{ins.root_cause_title}' | Uncertainty: {ins.uncertainty}")
        self.assertEqual(ins.root_cause_title, "Insufficient Evidence")
        self.assertEqual(ins.uncertainty, "INSUFFICIENT_EVIDENCE")
        self.assertEqual(len(ins.supporting_evidence_ids), 0)

    def test_antifraud_hallucination_rejection(self):
        print("\n=== Test 4: Verify Output Parser Hallucination Rejection ===")
        malicious_llm_payload = {
            "hypotheses": [
                {
                    "hypothesis_id": "hyp-fake-01",
                    "title": "Hallucinated Network Breach",
                    "description": "Attackers hijacked inference endpoints using custom memory exploit.",
                    "supporting_evidence_ids": ["ev-hallucinated-hash-999"],
                    "uncertainty": "LOW"
                }
            ]
        }
        with self.assertRaises(UnsupportedEvidenceError) as ctx:
            SynthesisOutputParser.parse_and_validate(
                raw_output=malicious_llm_payload,
                investigation_id=self.inv_id,
                repository=self.store
            )
        print("Successfully trapped hallucinated evidence reference:", str(ctx.exception))

        malformed_json_payload = "I think the model broke because of high load."
        with self.assertRaises(MalformedOutputError) as ctx2:
            SynthesisOutputParser.parse_and_validate(
                raw_output=malformed_json_payload,
                investigation_id=self.inv_id,
                repository=self.store
            )
        print("Successfully trapped unformatted natural language string:", str(ctx2.exception))
        print("[APPROVED] Strict anti-hallucination and validation schema gates functioning perfectly!")

if __name__ == "__main__":
    unittest.main()
