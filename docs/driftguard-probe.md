# DriftGuard Probe

DriftGuard Probe is a real-time investigation and decision engine. It operates directly on live operational and machine learning systems to autonomously investigate anomalies, model drift, and system alerts.

## Purpose
To connect directly with the DriftGuard ML platform, consume live telemetry (drift metrics, prediction logs, latency spikes), and orchestrate a multi-agent workflow to autonomously determine root causes, evaluate confidence, and suggest or execute remediation (e.g., retraining pipelines).

## Architecture & Major Components
The application is structured entirely around its core reasoning engine (`probe/`).

* **`probe/agents/`**: Contains the implementations of all specialized agents (Planner, Supervisor, Causal, Evaluator, Remediation, Compliance, Validation, Investigator, Researcher, Hypothesis, Architect, Critic, Reporter, Experimenter).
* **`probe/workflows/`**: Defines orchestrated sequences of agent interactions (`investigation.py`, `retraining.py`, `compliance.py`, `base.py`).
* **`probe/tools/`**: Exposes functional capabilities to the agents (e.g., `monitoring.py` for fetching drift stats, `execution/dispatch_pipeline.py` for kicking off Airflow dags, `forensic/` for historical comparisons).
* **`probe/reasoning/`**: The core logic for synthesizing outputs, parsing agent responses, and maintaining the deterministic reasoning pipeline.
* **`probe/services/`**: Supporting business logic like telemetry correlation (`correlation.py`).
* **`probe/providers/`**: Adapters to external LLMs and the main DriftGuard infrastructure (`adapters/driftguard.py`).
* **`probe/storage/`**: The memory and evidence repository (`repository.py` with `InMemoryEvidenceStore`).

## Execution Flow & Runtime Lifecycle
1. **Trigger**: An event (webhook from DriftGuard SDK, chron job, or manual trigger via `run_first_real_investigation.py`) initiates a workflow.
2. **Planning**: The Supervisor Agent receives the context and invokes the Planner Agent to decompose the alert into tasks.
3. **Execution**: The Investigator and Researcher tools fetch live data via MCP plugins and Adapters.
4. **Reasoning**: The Hypothesis and Causal agents synthesize the findings. The Critic challenges the findings, and the Evaluator scores confidence.
5. **Remediation**: If confidence thresholds are met, the Validation and Compliance agents vet the proposed action (e.g., model retraining) before the Remediation agent executes it via tools.
6. **Reporting**: The Reporter agent finalizes the investigation log.

## Entry Points
Development and local testing are driven through the primary entry point script:
```bash
cd apps/driftguard-probe
python run_first_real_investigation.py
```
This script acts as the main testing harness to simulate a live drift event and trigger the agent orchestration pipeline.

## Configuration & Dependencies
- Configured heavily via `.env` (referenced in `.env.example`).
- Dependencies managed in `pyproject.toml` and `requirements.txt`.
- Built to interact with MCP (Model Context Protocol) plugins for standardized tool integration.

## Current Capabilities & Limitations
- **Capabilities**: Highly sophisticated multi-agent orchestration; ability to actually execute retrain pipelines autonomously; robust causal validation layer.
- **Limitations**: Currently relies heavily on in-memory evidence storage (`InMemoryEvidenceStore`); persistence across severe application crashes requires further state management implementation.
