from abc import ABC, abstractmethod
from typing import Dict, List, Any

class ProviderAdapter(ABC):
    """
    Abstract base interface required for all monitoring platform integrations.
    Decouples Probe entirely from proprietary monitoring vendor SDKs or schemas.
    """
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    def fetch_model_details(self, model_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def fetch_model_versions(self, model_id: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def fetch_audit_logs(self, model_id: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def fetch_drift_history(self, model_id: str, limit: int = 500) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def fetch_retraining_history(self, model_id: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def fetch_system_metrics(self, model_id: str) -> List[Dict[str, Any]]:
        pass
