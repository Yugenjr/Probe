# Multi-Agent Roster & Responsibilities

Probe utilizes an orchestrated team of single-responsibility agents defined under `probe/agents/`. Every agent implements `BaseAgent` and communicates purely via structured Pydantic v2 schemas.

## Current Active Agents
- **`SupervisorAgent`**: Selects and oversees execution of domain workflows. Never performs direct investigation work.
- **`InvestigatorAgent`**: Extracts quantitative metrics, model metadata, and baseline statistical comparisons via Tools.
- **`ResearcherAgent`**: Interacts with memory retriever infrastructure and enterprise documentation search tools.
- **`HypothesisAgent`**: Analyzes disparate evidence items to generate testable fault theories and root-cause likelihoods.
- **`ExperimenterAgent`**: Designs validation experiments (e.g., historical replay, slice analysis) to test active hypotheses.
- **`EvaluatorAgent`**: Assesses evidence strength, SLA compliance, and remediation viability.
- **`ReporterAgent`**: Generates comprehensive, executive-ready diagnostic reports.
- **`MemoryAgent`**: Orchestrates memory infrastructure (`store`, `retriever`, `summarizer`, `embeddings`) without acting as a direct reasoning agent.

## Planned Roster Extensions
- **`PlannerAgent`**: Specialized in high-level resource estimation and task graph partitioning.
- **`ComplianceAgent`**: Validates proposals against regulatory and privacy governance policies.
- **`CriticAgent`**: Adversarially challenges hypotheses to eliminate confirmation bias.
