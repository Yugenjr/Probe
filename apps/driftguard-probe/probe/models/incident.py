"""Backwards-compatible legacy model alias re-exporting v2.0 domain Incident models."""
from ..domain.incident import Incident, IncidentSeverity, IncidentStatus

__all__ = ["Incident", "IncidentSeverity", "IncidentStatus"]
