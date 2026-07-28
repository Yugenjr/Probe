# Probe Platform Overview

Probe is a unified, AI-native Multi-Agent Investigation Platform designed to bridge the gap between raw diagnostic data (logs, telemetry, documents) and actionable decision intelligence. 

## Purpose
The primary objective of Probe is to automate complex reasoning and root cause analysis across both historical and live operational environments. Rather than relying on simple text generation or basic LLM wrappers, Probe employs specialized, role-based AI agents that collaborate to navigate systems, validate hypotheses against evidence, and produce structured, high-confidence investigation reports.

## Core Capabilities
* **Multi-Agent Orchestration:** A distributed intelligence architecture where agents (like the Planner, Investigator, Causal Analyst, and Evaluator) collaborate to solve complex incidents.
* **Deterministic Reasoning Validation:** The platform mathematically and chronologically validates hypotheses against concrete evidence timelines rather than relying on LLM intuition.
* **Unified Investigations:** Capable of handling post-mortem forensics (PDFs, log dumps, support tickets) as well as real-time telemetry (Prometheus metrics, model drift).
* **Automated Remediation:** Beyond analysis, the platform can formulate and execute corrective actions on live infrastructure (via the Remediation Agent) while adhering to defined boundaries (via the Compliance and Validation Agents).

## High-Level Architecture
The Probe platform is built as a monorepo consisting of two primary applications powered by a shared Software Development Kit (SDK):

1. **Decision Probe** (`apps/decision-probe`): A batch-processing, RAG-heavy application for historical incident investigations.
2. **DriftGuard Probe** (`apps/driftguard-probe`): A real-time, event-driven engine connecting to live telemetry and ML monitoring systems.
3. **DriftGuard SDK** (`packages/driftguard-sdk`): The foundational runtime, governance, monitoring, and validation layer used by both applications.

## Key Differentiators
- **Evidence-Grounded:** Conclusions are strictly tethered to verifiable artifacts, actively minimizing hallucination.
- **Auditable Workflows:** The multi-agent interactions are traced and logged, providing a clear chain of reasoning.
- **Enterprise Ready:** Incorporates governance, compliance checks, and human-in-the-loop review gates out of the box.
