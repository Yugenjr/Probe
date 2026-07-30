# Architecture Decision Record (ADR) 001: Core Architecture Principles

## Context and Problem Statement
DriftGuard Probe has evolved from a collection of isolated agents into a full-fledged AI incident investigation platform. We needed to solidify our architectural principles to ensure that as the platform grows, the separation of concerns remains pristine, state mutations are tightly controlled, and testing continues to be reliable. We also needed to solve the architectural problem of applying long-term memory across investigations.

## Decision

We have adopted the following strict architectural principles across the platform:

1. **Deterministic Services vs. LLM Agents:**
   - **Deterministic Services** (e.g., `EvidenceGraphBuilder`, `EvidenceRanker`, `EvidenceCollector`) are strictly responsible for gathering, preparing, formatting, and ranking information. They do not execute LLM inferences.
   - **LLM Agents** (e.g., `CausalSynthesisAgent`, `AdversarialCriticAgent`) are strictly responsible for interpreting that information and reasoning over it.
   - *Rationale:* Decoupling data preparation from reasoning avoids injecting unpredictable LLM logic into deterministic data flows, simplifying testing and increasing reliability.

2. **The Supervisor is the Sole Owner of Orchestration:**
   - Agents (like the `AdversarialCriticAgent`) no longer dictate retry loops or pipeline execution. Agents produce information.
   - The **Supervisor** receives these reports and makes all the routing decisions (e.g., whether to loop back for more evidence or advance to the next stage).
   - The **Orchestrator** is a runtime engine that validates and executes the Supervisor's commands securely via state transitions on the `InvestigationSession`.
   - *Rationale:* Centralizing control flow prevents infinite loops, duplicate orchestration logic, and conflicting agent decisions.

3. **Agents Must Remain Stateless:**
   - Agents do not hold internal state, mutate the `InvestigationSession` directly in hidden ways, or retain memory across invocations.
   - State is explicitly passed into them via arguments (e.g., `HistoricalPatternAnalysis`, `EvidenceBundle`), and they return immutable Pydantic artifacts.
   - *Rationale:* Prevents hidden side-effects and makes unit testing trivial.

4. **Bidirectional Memory as a Capability:**
   - Memory is not an investigation stage. It is a capability exposed via the `MemoryBackend` interface (abstracting Neo4j, Qdrant, etc.) and managed by dedicated agents.
   - **Memory Recall:** Executes during `PLANNING` before evidence collection to pull `HistoricalPatternAnalysis`, identifying if the problem has been solved before.
   - **Memory Learn:** Executes at the conclusion of `DECISION` to persist the `InvestigationRecord` and real-world `OutcomeFeedback`.
   - *Rationale:* Embedding memory recall in planning allows the platform to intelligently narrow its search space early. Appending memory learn at the end creates a continuous improvement flywheel.

5. **Structural Versioning for Artifacts:**
   - All domain schemas (e.g., `EvidenceBundle`, `CausalHypothesis`, `InvestigationResult`) and archives (`InvestigationRecord`) now include a hardcoded `schema_version` (e.g., `"1.0.0"`).
   - *Rationale:* Ensures backwards compatibility for our data lake, historical retrieval graphs, and analytics reporting.

## Consequences
- **Positive:** We have a highly modular, predictable, and fully typed reasoning pipeline. Parallel evidence collection speeds up triage, and we have a clear pattern for adding new tools or domain models without breaking the orchestrator.
- **Negative/Trade-offs:** Passing all state explicitly via `InvestigationSession` and using strict Pydantic models increases boilerplate. Implementing new agents requires adherence to strict interface contracts.
