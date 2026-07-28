"""Backwards compatible re-export of standalone DriftGuardAdapter."""
from probe_adapters.driftguard.client import DriftGuardAdapter, DriftGuardRESTClient

__all__ = ["DriftGuardAdapter", "DriftGuardRESTClient"]
