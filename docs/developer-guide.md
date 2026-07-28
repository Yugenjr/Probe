# Developer Guide & Architecture Review

This document outlines the architectural health of the Probe repository and serves as a guide for future contributors.

## Architecture Review

### Strengths
- **Clear Module Boundaries**: The separation of the SDK (`packages/driftguard-sdk`) from the applications (`apps/`) is strictly maintained. The applications do not import from one another, preventing circular dependencies.
- **Agent Abstraction**: Agents in `driftguard-probe/probe/agents/` inherit from a clean `BaseAgent`, making the addition of new agents highly modular.
- **Robust Database Initialization**: The SDK `main.py` contains excellent automatic schema migration logic that gracefully handles the transition from single-key to composite-key tables without catastrophic failure.

### Technical Debt & Potential Bugs
- **Persistence Fragility in DriftGuard Probe**: The real-time engine heavily relies on `InMemoryEvidenceStore` (`probe/storage/repository.py`). If the application crashes during a long-running causal analysis, the investigation state is lost. This needs to be abstracted to Redis or PostgreSQL.
- **Redundant Schema Definitions**: There is some overlap between Pydantic schemas defined in the SDK (`packages/driftguard-sdk/main.py`) and those defined in `driftguard-probe/probe/schemas/api.py`. These should be unified within the SDK.
- **Missing Abstractions**: The Decision Probe inference loop lacks a generic streaming adapter. It currently relies heavily on specific RAG implementations, making it difficult to swap out embedding models without touching core logic.
- **Duplicate Code**: Telemetry correlation logic in `driftguard-probe/probe/services/correlation.py` partially duplicates metrics formatting found in the SDK.

### Opportunities for Modularisation
- **Extract Workflows**: The workflows in `probe/workflows/` could be abstracted into a declarative YAML/JSON format rather than hardcoded Python classes, allowing non-engineers to define investigation pipelines.
- **SDK Routing**: The `main.py` in the SDK is currently 1,300+ lines long. While it mentions "remaining routes migrated to routers/", there is still a massive amount of logic (auth, db initialization, endpoints) in a single file that should be split into `routers/`, `models/`, and `core/` modules.

## Contribution Guidelines
- Do not modify `apps/decision-probe` to directly import from `apps/driftguard-probe`. Always push shared logic down to `packages/driftguard-sdk`.
- Ensure new AI agents implement the `BaseAgent` interface and explicitly declare their inputs and outputs for the Supervisor.
