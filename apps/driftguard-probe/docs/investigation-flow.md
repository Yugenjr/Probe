# Autonomous Investigation Flow

When an incident (such as model drift, quality degradation, or latency spike) occurs in production, Probe executes the following autonomous reasoning loop:

1. **Incident Reception (`IncidentCreated`)**: A webhook payload arrives at `POST /api/v1/webhooks`. The Gateway parses it into an `Incident` model and spawns a new `InvestigationState` in the `Created` stage.
2. **Supervisor Routing (`Workflow Selection`)**: The Supervisor examines the incident context and picks an appropriate domain workflow (e.g., `DriftInvestigationWorkflow` vs `RetrainingWorkflow`).
3. **Evidence Collection (`CollectingEvidence`)**: The Investigator agent queries historical metrics, feature distributions, and recent audit logs via Tool invocations.
4. **Knowledge Retrieval (`Researching`)**: The Researcher agent probes organizational documentation and past incident memos using Memory infrastructure.
5. **Hypothesis Formulation (`GeneratingHypothesis`)**: The Hypothesis agent synthesizes accrued evidence into concrete root-cause theories.
6. **Experimentation (`PlanningExperiments`)**: The Experimenter designs mock tests or sandbox evaluation criteria to validate hypotheses.
7. **Evaluation (`Evaluating`)**: The Evaluator scores experimental outcomes against SLA criteria.
8. **Reporting (`Reporting`)**: The Reporter constructs a structured markdown/JSON artifact detailing validated root causes and proposed remediations for human review.
