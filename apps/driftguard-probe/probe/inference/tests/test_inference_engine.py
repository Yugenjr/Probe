import unittest
import json
import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from probe.investigation.service import InvestigationService
from probe.providers.adapters.driftguard import DriftGuardAdapter
from probe.context.builder import ContextBuilder
from probe.evidence.extractor import EvidenceExtractor
from probe.storage.repository import InMemoryEvidenceStore
from probe.graph.builder import EvidenceGraphBuilder
from probe.reasoning.synthesis.planner import ReasoningPlanner
from probe.inference import (
    InferenceConfig, InferenceClient, InferencePromptBuilder, TelemetryCollector,
    InferenceTimeoutError, InferenceBackendError, MalformedResponseError,
    SchemaValidationError, EvidenceHallucinationError
)

# Dummy target Pydantic schema for tests
class MockHypothesis(BaseModel):
    title: str
    description: str
    supporting_evidence_ids: List[str] = Field(default_factory=list)

class MockHypothesisList(BaseModel):
    hypotheses: List[MockHypothesis]

class TestInferenceEngineProduction(unittest.TestCase):
    def setUp(self):
        self.inv_service = InvestigationService()
        self.inv_id = self.inv_service.create_investigation(target_resource_id="fraud-v2")
        self.adapter = DriftGuardAdapter()
        self.context = ContextBuilder(self.adapter).build_context(self.inv_id, "fraud-v2")
        self.store = InMemoryEvidenceStore()
        for ev in EvidenceExtractor().extract_all_evidence(self.context):
            self.store.append(ev)
        self.topology = EvidenceGraphBuilder(self.store).build_graph(self.inv_id)
        self.plan = ReasoningPlanner.create_plan(self.inv_id, self.context, self.topology, self.store)
        
        # Grab a real evidence ID from storage for valid tests
        items = self.store.get_by_investigation(self.inv_id)
        self.valid_id_1 = items[0].id
        self.valid_id_2 = items[1].id
        
        self.prompt_bundle = InferencePromptBuilder.build_prompt(
            plan=self.plan,
            context=self.context,
            repository=self.store,
            target_schema=MockHypothesisList,
            domain_instructions="Synthesize incident hypotheses."
        )

    def test_1_successful_structured_output(self):
        print("=== Test 1: Successful Structured Pydantic Generation ===")
        def mock_transport(req: Dict[str, Any], timeout: float) -> str:
            return json.dumps({
                "hypotheses": [
                    {
                        "title": "Verified Demographics Shift",
                        "description": "Covariate age feature distribution changed.",
                        "supporting_evidence_ids": [self.valid_id_1, self.valid_id_2]
                    }
                ]
            })

        collector = TelemetryCollector()
        config = InferenceConfig(model_identifier="vLLM/Llama-3.1-70B", max_retries=2, retry_base_delay_seconds=0.05)
        client = InferenceClient(config=config, telemetry_collector=collector, transport_override=mock_transport)
        
        result = client.generate(self.prompt_bundle, target_schema=MockHypothesisList, evidence_repository=self.store)
        
        self.assertIsInstance(result.artifact, MockHypothesisList)
        self.assertEqual(len(result.artifact.hypotheses), 1)
        self.assertEqual(result.artifact.hypotheses[0].supporting_evidence_ids, [self.valid_id_1, self.valid_id_2])
        self.assertEqual(result.retry_count, 0)
        print(f"Generated validated Pydantic object cleanly! Telemetry latency: {result.latency_ms}ms")

    def test_2_exponential_backoff_retry_recovery(self):
        print("\n=== Test 2: Exponential Backoff Retry Recovery (Transient 503 Failure) ===")
        call_count = {"calls": 0}
        def fail_then_succeed(req: Dict[str, Any], timeout: float) -> str:
            call_count["calls"] += 1
            if call_count["calls"] < 3:
                raise InferenceBackendError("HTTP 503 Service Unavailable (GPU node overloaded)")
            return json.dumps({"hypotheses": [{"title": "Recovered Output", "description": "Success after retries", "supporting_evidence_ids": [self.valid_id_1]}]})

        config = InferenceConfig(max_retries=3, retry_base_delay_seconds=0.05)
        client = InferenceClient(config=config, transport_override=fail_then_succeed)
        
        result = client.generate(self.prompt_bundle, target_schema=MockHypothesisList, evidence_repository=self.store)
        self.assertEqual(call_count["calls"], 3)
        self.assertEqual(result.retry_count, 2)
        print("Successfully recovered on attempt 3 after exponential backoff!")

    def test_3_malformed_json_and_empty_response_rejection(self):
        print("\n=== Test 3: Malformed JSON and Empty Response Rejection ===")
        def empty_transport(req: Dict[str, Any], timeout: float) -> str:
            return ""

        config = InferenceConfig(max_retries=1, retry_base_delay_seconds=0.01)
        client_empty = InferenceClient(config=config, transport_override=empty_transport)
        
        with self.assertRaises(InferenceBackendError) as ctx:
            client_empty.generate(self.prompt_bundle, target_schema=MockHypothesisList, evidence_repository=self.store)
        self.assertIsInstance(ctx.exception.__cause__, MalformedResponseError)
        print("Successfully trapped empty response as MalformedResponseError.")

        def malformed_transport(req: Dict[str, Any], timeout: float) -> str:
            return "{ bad json syntax ... [}"
        client_malformed = InferenceClient(config=config, transport_override=malformed_transport)
        with self.assertRaises(InferenceBackendError) as ctx2:
            client_malformed.generate(self.prompt_bundle, target_schema=MockHypothesisList, evidence_repository=self.store)
        print("Successfully trapped malformed syntax without breaking reasoning loop.")

    def test_4_schema_validation_and_required_fields_gate(self):
        print("\n=== Test 4: Schema Validation (Missing Required Attributes) ===")
        def invalid_schema_transport(req: Dict[str, Any], timeout: float) -> str:
            # Missing mandatory 'description' field
            return json.dumps({"hypotheses": [{"title": "Incomplete Hypothesis"}]})

        config = InferenceConfig(max_retries=1, retry_base_delay_seconds=0.01)
        client = InferenceClient(config=config, transport_override=invalid_schema_transport)
        
        with self.assertRaises(InferenceBackendError) as ctx:
            client.generate(self.prompt_bundle, target_schema=MockHypothesisList, evidence_repository=self.store)
        self.assertIsInstance(ctx.exception.__cause__, SchemaValidationError)
        print("Successfully rejected incomplete output via SchemaValidationError:", str(ctx.exception.__cause__))

    def test_5_evidence_id_hallucination_rejection(self):
        print("\n=== Test 5: Strict Evidence ID Hallucination Rejection (No Silent Repair) ===")
        def hallucinating_transport(req: Dict[str, Any], timeout: float) -> str:
            return json.dumps({
                "hypotheses": [
                    {
                        "title": "Hallucinated Claim",
                        "description": "Model weights became corrupted by Cosmic Rays.",
                        "supporting_evidence_ids": ["ev-hallucinated-fake-id-888", self.valid_id_1]
                    }
                ]
            })

        config = InferenceConfig(max_retries=1, retry_base_delay_seconds=0.01)
        client = InferenceClient(config=config, transport_override=hallucinating_transport)
        
        with self.assertRaises(InferenceBackendError) as ctx:
            client.generate(self.prompt_bundle, target_schema=MockHypothesisList, evidence_repository=self.store)
        self.assertIsInstance(ctx.exception.__cause__, EvidenceHallucinationError)
        print("Successfully rejected hallucinated evidence reference without silent repair!")
        print("Trap message:", str(ctx.exception.__cause__))

    def test_6_timeout_and_large_response_handling(self):
        print("\n=== Test 6: Timeout and Large Response Capacity Verification ===")
        def timeout_transport(req: Dict[str, Any], timeout: float) -> str:
            raise TimeoutError("Simulated GPU inference socket timeout.")

        config = InferenceConfig(timeout_seconds=0.1, max_retries=1, retry_base_delay_seconds=0.01)
        client_timeout = InferenceClient(config=config, transport_override=timeout_transport)
        with self.assertRaises(InferenceBackendError) as ctx:
            client_timeout.generate(self.prompt_bundle, target_schema=MockHypothesisList, evidence_repository=self.store)
        self.assertIsInstance(ctx.exception.__cause__, InferenceTimeoutError)
        print("Successfully trapped InferenceTimeoutError on hung GPU socket.")

        # Test large response capacity (e.g. 50+ items)
        def large_transport(req: Dict[str, Any], timeout: float) -> str:
            items = []
            for i in range(50):
                items.append({
                    "title": f"Large Scale Anomaly Cluster #{i+1}",
                    "description": f"Exhaustive feature telemetry check on dimension #{i+1}",
                    "supporting_evidence_ids": [self.valid_id_1]
                })
            return json.dumps({"hypotheses": items})
            
        client_large = InferenceClient(config=InferenceConfig(max_retries=1), transport_override=large_transport)
        res_large = client_large.generate(self.prompt_bundle, target_schema=MockHypothesisList, evidence_repository=self.store)
        self.assertEqual(len(res_large.artifact.hypotheses), 50)
        print(f"Successfully processed large response buffer ({res_large.token_usage_approx} approx tokens).")

    def test_7_telemetry_security_audit(self):
        print("\n=== Test 7: Operational Telemetry Security Audit (Zero Secret / Payload Leakage) ===")
        collector = TelemetryCollector()
        secret_token = "secret-super-sensitive-api-key-9999"
        config = InferenceConfig(authentication_token=secret_token, model_identifier="NVIDIA/NIM-v3", max_retries=1)
        
        def simple_transport(req: Dict[str, Any], timeout: float) -> str:
            return json.dumps({"hypotheses": [{"title": "Safe Operational Output", "description": "No secrets logged", "supporting_evidence_ids": [self.valid_id_1]}]})

        client = InferenceClient(config=config, telemetry_collector=collector, transport_override=simple_transport)
        client.generate(self.prompt_bundle, target_schema=MockHypothesisList, evidence_repository=self.store)

        records = collector.get_records()
        self.assertEqual(len(records), 1)
        rec = records[0]
        print(f"Recorded Telemetry Record ID: {rec.record_id} | Success: {rec.success} | Duration: {rec.request_duration_ms}ms")
        self.assertEqual(rec.model_identifier, "NVIDIA/NIM-v3")

        # SECURITY VERIFICATION: Prove secret auth token or sensitive investigation strings are NOT in telemetry memory logs!
        is_secure = collector.verify_no_secrets_leaked(
            secret_token=secret_token,
            sensitive_payload_keywords=["fraud_v1.csv", "account_balance", "customer_demographic", "tx_volume", "inv-fraud-v2"]
        )
        self.assertTrue(is_secure, "SECURITY VIOLATION: Auth tokens or sensitive evidence payloads leaked into operational telemetry!")
        print("[APPROVED] Operational telemetry audited: Zero secret authentication tokens or investigation evidence payloads leaked!")


if __name__ == "__main__":
    unittest.main()
