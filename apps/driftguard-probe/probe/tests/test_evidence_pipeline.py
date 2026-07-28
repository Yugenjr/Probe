import sys
import unittest
from probe.investigation.service import InvestigationService
from probe.investigation.states import InvestigationStatus
from probe.providers.adapters.driftguard import DriftGuardAdapter
from probe.context.builder import ContextBuilder
from probe.evidence.extractor import EvidenceExtractor
from probe.storage.repository import InMemoryEvidenceStore
from probe.graph.builder import EvidenceGraphBuilder

class TestDeterministicEvidencePipeline(unittest.TestCase):
    def test_end_to_end_idempotent_execution_trace(self):
        print("=== Step 1: Initialize Investigation Service & Assign ID ===")
        inv_service = InvestigationService()
        inv_id = inv_service.create_investigation(target_resource_id="fraud-v2", tenant_id="prod-east")
        self.assertTrue(inv_id.startswith("inv-fraud-v2-"))
        print(f"Created Investigation ID: {inv_id}")

        print("\n=== Step 2: Invoke Provider Adapter (DriftGuard) via Dependency Inversion ===")
        adapter = DriftGuardAdapter()
        self.assertEqual(adapter.provider_name, "DriftGuard-Core-v3")

        print("\n=== Step 3: Build Immutable InvestigationContext ===")
        ctx_builder = ContextBuilder(adapter)
        context = ctx_builder.build_context(investigation_id=inv_id, target_model_id="fraud-v2")
        self.assertEqual(context.model_version, "1.2.0")
        self.assertEqual(context.model["status"], "degraded")
        print(f"InvestigationContext built successfully. Active Model Version: {context.model_version}")

        print("\n=== Step 4: Execute Deterministic Evidence Extractor (Idempotency Gate) ===")
        extractor = EvidenceExtractor()
        evidence_run_1 = extractor.extract_all_evidence(context)
        print(f"Extracted {len(evidence_run_1)} typed Evidence objects on Run 1.")

        # Execute extraction a second time on identical context to prove determinism
        evidence_run_2 = extractor.extract_all_evidence(context)
        print(f"Extracted {len(evidence_run_2)} typed Evidence objects on Run 2.")

        # PROOF OF IDEMPOTENCY: Assert all IDs and cryptographic SHA-256 hashes match identically!
        for e1, e2 in zip(evidence_run_1, evidence_run_2):
            self.assertEqual(e1.id, e2.id, "Deterministic ID mismatch between extraction runs!")
            self.assertEqual(e1.hash, e2.hash, "Cryptographic SHA-256 hash mismatch!")
            self.assertEqual(e1.type, e2.type)
        print("[APPROVED] Complete Idempotency verified: Both runs produced identical SHA-256 signatures and IDs!")

        print("\n=== Step 5: Persist in Append-Only Evidence Store ===")
        store = InMemoryEvidenceStore()
        for ev in evidence_run_1:
            added = store.append(ev)
            self.assertTrue(added)

        # Appending the duplicate Run 2 items must safely return False without error or mutation
        for ev in evidence_run_2:
            added = store.append(ev)
            self.assertFalse(added, "Duplicate evidence should converge cleanly as no-op!")
        print(f"Evidence store holds exactly {len(store.get_by_investigation(inv_id))} unique records after double ingestion.")

        print("\n=== Step 6: Build Topological Evidence Graph for Future Reasoning Agents ===")
        graph_builder = EvidenceGraphBuilder(store)
        topology = graph_builder.build_graph(investigation_id=inv_id)
        print(f"Evidence Graph assembled: {len(topology.nodes)} Nodes | {len(topology.edges)} Directed Edges")
        self.assertGreater(len(topology.nodes), 0)
        self.assertGreater(len(topology.edges), 0)

        inv_service.update_status(inv_id, InvestigationStatus.EVIDENCE_READY, reason="Graph compiled successfully.")
        print(f"Final Investigation Status: {inv_service.get_investigation(inv_id).status}")

if __name__ == "__main__":
    unittest.main()
