# AI Agents

Probe utilizes a specialized, multi-agent architecture where distinct agents collaborate to resolve complex investigations. The implementations for these agents are primarily located in `apps/driftguard-probe/probe/agents/`.

## Agent Catalog

### Planner Agent (`planner.py`)
- **Purpose**: Deconstructs high-level user objectives or system alerts into sequential, actionable investigation steps.
- **Inputs**: Raw alert telemetry, user requests.
- **Outputs**: A structured investigation plan (JSON/YAML).
- **Dependencies**: Memory Agent.
- **Status**: Implemented.

### Architect Agent (`architect.py`)
- **Purpose**: Analyzes structural dependencies and system topologies to provide architectural context.
- **Inputs**: System graphs, microservice maps.
- **Outputs**: Topology context appended to the plan.
- **Dependencies**: Memory Agent, external infrastructure APIs.
- **Status**: Implemented.

### Investigator Agent (`investigator.py`)
- **Purpose**: Navigates environments and queries systems to gather required data based on the plan.
- **Inputs**: Sub-tasks from Planner.
- **Outputs**: Raw metric logs and queried states.
- **Dependencies**: Tools (`probe/tools/`), Memory Agent.
- **Status**: Implemented.

### Researcher Agent (`researcher.py`)
- **Purpose**: Performs deep contextual retrieval across documents, wikis, and historical incident records.
- **Inputs**: Keywords from the Investigator or Planner.
- **Outputs**: Relevant historical text snippets and runbooks.
- **Dependencies**: Retrieval Engine (Vector DB).
- **Status**: Implemented.

### Hypothesis Agent (`hypothesis.py`)
- **Purpose**: Synthesizes available evidence to formulate potential root causes and contributing factors.
- **Inputs**: Aggregated evidence from Investigator and Researcher.
- **Outputs**: A list of structured hypotheses.
- **Dependencies**: Memory Agent.
- **Status**: Implemented.

### Causal Agent (`causal.py`)
- **Purpose**: Validates hypotheses against the evidence timeline to establish definitive cause-and-effect relationships.
- **Inputs**: Hypotheses and Timeline data.
- **Outputs**: Validated causal links or rejected hypotheses.
- **Dependencies**: Deterministic reasoning engine (`probe/reasoning/`).
- **Status**: Implemented.

### Critic Agent (`critic.py`)
- **Purpose**: Challenges proposed hypotheses and reasoning chains to eliminate bias and logical fallacies.
- **Inputs**: Causal validations.
- **Outputs**: Critiques and required plan revisions.
- **Dependencies**: Memory Agent.
- **Status**: Implemented.

### Evaluator Agent (`evaluator.py`)
- **Purpose**: Quantifies the confidence level of conclusions based on evidence quality and reasoning validity.
- **Inputs**: Final hypotheses post-critique.
- **Outputs**: Numerical confidence scores.
- **Dependencies**: Memory Agent.
- **Status**: Implemented.

### Reporter Agent (`reporter.py`)
- **Purpose**: Compiles findings, timelines, and remediation steps into structured, human-readable reports.
- **Inputs**: Final verified conclusions and confidence scores.
- **Outputs**: Markdown/PDF reports.
- **Dependencies**: None.
- **Status**: Implemented.

### Supervisor Agent (`supervisor.py`)
- **Purpose**: Orchestrates the agent collective, managing state, routing tasks, and ensuring adherence to the investigation plan.
- **Inputs**: Global state and outputs from all agents.
- **Outputs**: Execution commands to other agents.
- **Dependencies**: All agents.
- **Status**: Implemented.

### Memory Agent (`memory.py`)
- **Purpose**: Maintains short-term context and long-term investigation history for stateful reasoning.
- **Inputs**: Read/Write requests from all reasoning agents.
- **Outputs**: Historical context.
- **Dependencies**: `probe/storage/repository.py`.
- **Status**: Implemented.

### Validation Agent (`validation.py`)
- **Purpose**: Performs final integrity and safety checks before producing decisions or outputs.
- **Inputs**: Proposed remediation actions.
- **Outputs**: Approval boolean or rejection reason.
- **Dependencies**: Supervisor Agent.
- **Status**: Implemented.

### Compliance Agent (`compliance.py`)
- **Purpose**: Ensures proposed actions and investigations adhere to organizational policies and regulatory standards.
- **Inputs**: Proposed remediation actions.
- **Outputs**: Policy compliance flags.
- **Dependencies**: Supervisor Agent.
- **Status**: Implemented.

### Remediation Agent (`remediation.py`)
- **Purpose**: Formulates and executes automated corrective actions on live infrastructure (e.g., triggering retraining).
- **Inputs**: Validated and compliant decision plans.
- **Outputs**: Executed webhook calls or API requests.
- **Dependencies**: `probe/tools/execution/`.
- **Status**: Implemented.

## Communication Pattern
Agents do not typically call each other directly (except via the `Memory Agent`). Instead, the **Supervisor Agent** orchestrates the flow, routing the output of one agent as the input to the next according to the predefined workflows in `probe/workflows/`.
