"""Exclusive 3-Agent Cognitive Reasoning Roster and backwards compatible legacy exports."""
from .base import BaseAgent
from .causal import CausalSynthesisAgent
from .critic import AdversarialCriticAgent
from .architect import InterventionArchitectAgent

# Backward compatibility imports for v2.0 and legacy tests
from .investigator import InvestigatorAgent
from .researcher import ResearcherAgent
from .hypothesis import HypothesisAgent
from .validation import ValidationAgent, CriticAgent, EvaluatorAgent, ComplianceAgent
from .remediation import RemediationAgent, ExperimenterAgent
from .memory import MemoryAgent
from .planner import PlannerAgent
from .supervisor import SupervisorAgent

__all__ = [
    "BaseAgent",
    # V3.0 Exclusive 3-Agent Cognitive Reasoning Roster
    "CausalSynthesisAgent",
    "AdversarialCriticAgent",
    "InterventionArchitectAgent",
    # Backward compatibility exports
    "InvestigatorAgent",
    "ResearcherAgent",
    "HypothesisAgent",
    "ValidationAgent",
    "RemediationAgent",
    "CriticAgent",
    "EvaluatorAgent",
    "ComplianceAgent",
    "ExperimenterAgent",
    "MemoryAgent",
    "PlannerAgent",
    "SupervisorAgent",
]
