"""Governance audit and validation check interface protocol definition."""
from typing import Any, Dict, List, Protocol, Union, runtime_checkable
from .context import ResourceContext


@runtime_checkable
class GovernanceProvider(Protocol):
    """Protocol defining regulatory compliance, audit log extraction, and data schema checks.
    
    Separated from basic observability to respect Interface Segregation Principle (ISP).
    """
    async def get_validation_records(self, target: Union[str, ResourceContext]) -> List[Dict[str, Any]]:
        """Retrieve automated data test suite success/failure rates and schema rule verifications."""
        ...

    async def get_audit_logs(self, target: Union[str, ResourceContext], limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve chronological operational intervention logs, threshold overrides, and deploys."""
        ...

    async def get_reports(self, target: Union[str, ResourceContext]) -> List[Dict[str, Any]]:
        """Retrieve historical quarterly health reviews and investigation audit documentation."""
        ...
