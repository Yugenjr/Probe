# DriftGuard Probe Roadmap

## Phase 1: Reference Architecture & Skeleton (Current)
- Complete repository foundation and interface contract decoupling.
- Set up domain schemas, lifecycle state tracking, and plugin loaders.

## Phase 2: Core Adapter & LLM Harness
- Finalize reference `DriftGuardClient` with auto-retry and bearer auth.
- Integrate multi-provider LLM parser supporting OpenAI, Anthropic, and local Ollama inference.
- Connect asynchronous event bus with OpenTelemetry traces.

## Phase 3: Workflow Automation & Memory Engine
- Implement `DriftInvestigationWorkflow` and vector embedding retrieval mechanisms.
- Enable end-to-end webhook execution from simulated model incidents to human-readable markdown reports.

## Phase 4: MCP Native Server & Plugin Community
- Open public plugin marketplace for third-party MLOps monitoring adapters (WhyLabs, Arize, Evidently AI).
- Launch distributed worker execution for heavy experiment evaluation.
