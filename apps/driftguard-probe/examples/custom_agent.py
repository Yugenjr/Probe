"""Example demonstration showing how to define and register a third-party plugin agent."""
import asyncio
from typing import Any
from probe.agents.base import BaseAgent
from probe.core.state import InvestigationState
from probe.core.lifecycle import InvestigationStatus
from probe.core.registry.agent_registry import get_agent_registry
from probe.models.incident import Incident, IncidentSeverity


class CustomAuditAgent(BaseAgent):
    """Custom specialized reasoning agent that examines database permission records."""
    @property
    def role_name(self) -> str:
        return "CustomAuditAgent"

    async def execute(self, state: InvestigationState, **kwargs: Any) -> Any:
        print(f"[CustomAuditAgent] Executing specialized inspection for session {state.investigation_id}...")
        state.execution_history.append("CustomAuditAgent verified role-based access control compliance.")
        return {"audit_status": "PASSED"}


async def main():
    # Register agent dynamically without modifying core repository files
    registry = get_agent_registry()
    registry.register("custom_auditor", CustomAuditAgent)

    # Discover capabilities
    print("Available agents in dynamic registry:", registry.discover())

    # Instantiate and test run
    agent = registry.get("custom_auditor")
    dummy_incident = Incident(
        incident_id="inc-sample-001",
        model_id="customer_churn_v2",
        model_version="2.1.0",
        trigger_type="security_alert",
        severity=IncidentSeverity.HIGH,
    )
    state = InvestigationState(investigation_id="inv-sample-001", incident=dummy_incident)
    result = await agent.execute(state)
    print("Agent Execution Result:", result)


if __name__ == "__main__":
    asyncio.run(main())
