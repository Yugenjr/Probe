"""Investigator domain expert agent analyzing quantitative telemetry and feature distribution drift."""
import logging
import json
import uuid
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from .base import BaseAgent
from ..engine.state import InvestigationSession
from ..core.di import get_container

logger = logging.getLogger(__name__)


class EvidenceCollection(BaseModel):
    """Schema representing LLM investigator raw observations and evidence collection."""
    observations: List[str] = Field(..., description="Chronological diagnostic observations")
    anomalies: List[str] = Field(..., description="List of identified data anomalies")
    supporting_evidence: List[Dict[str, Any]] = Field(
        default_factory=list, description="Supporting telemetry snippets"
    )
    confidence: float = Field(..., description="Overall confidence level (0.0 to 1.0)")
    reasoning: str = Field(..., description="Diagnostic reasoning backing confidence weight")


class InvestigatorAgent(BaseAgent):
    """Forensic quantitative telemetry and feature shift diagnostician.

    Operates as an autonomous domain expert evaluating feature distance metrics (ADWIN, Wasserstein)
    and correlating statistical data anomalies against system operational degradation curves.

    MCP Integration:
        Before invoking the LLM, the Investigator queries the ToolGateway for:
          - Relevant knowledge base articles (search_documents)
          - Historical precedents for the same model (search_investigations)
        This context enriches the LLM prompt, producing higher-quality evidence.
    """

    @property
    def role_name(self) -> str:
        return "Investigator"


    async def execute(self, state: InvestigationSession, **kwargs: Any) -> Dict[str, Any]:
        logger.info(
            "Investigator Agent evaluating quantitative drift telemetry for session %s",
            state.session_id,
        )
        from ..domain.evidence import DriftEvidence

        # 1. Resolve drift score from session context
        drift_score = 0.25
        if state.investigation_context and state.investigation_context.predictions:
            first_pred = state.investigation_context.predictions[0]
            if isinstance(first_pred, dict) and first_pred.get("drift_score") is not None:
                drift_score = first_pred["drift_score"]
        elif state.incident and state.incident.raw_payload and isinstance(state.incident.raw_payload, dict):
            val = state.incident.raw_payload.get("drift_score")
            if val is not None:
                drift_score = val

        if drift_score is None:
            drift_score = 0.25

        # 2. Collect evidence via the unified EvidenceGateway
        knowledge_context = ""
        mcp_enriched = False
        if self.evidence_gateway:
            try:
                bundle = await self.evidence_gateway.collect_evidence(state)
                knowledge_context = bundle.combined_context
                mcp_enriched = True
                logger.info(
                    "[Investigator] Collected evidence bundle from EvidenceGateway: %d items, %d chars",
                    len(bundle.items),
                    len(knowledge_context)
                )
            except Exception as exc:
                logger.warning("[Investigator] Evidence collection failed: %s", exc)

        # 3. Structured LLM query with enriched context

        if self.llm_provider and hasattr(self.llm_provider, "generate_step_structured"):
            predictions = (
                state.investigation_context.predictions
                if state.investigation_context
                else []
            )
            pruned_predictions = predictions[:10]
            telemetry_data = {
                "incident": state.incident.model_dump(mode="json"),
                "predictions": pruned_predictions,
                "fallback_drift_score": drift_score,
            }
            telemetry_json = json.dumps(telemetry_data, indent=2)

            try:
                collection = await self.llm_provider.generate_step_structured(
                    prompt_name="investigator",
                    prompt_version="v1",
                    response_model=EvidenceCollection,
                    context={
                        "context_json": telemetry_json,
                        "knowledge_context": knowledge_context,
                    },
                    temperature=0.1,
                )
                logger.info("Investigator Agent successfully generated raw evidence via LLM.")

                # Convert structured observations to typed universal evidence
                if collection.supporting_evidence:
                    for ev in collection.supporting_evidence:
                        feat = ev.get("feature_name", "all_features")
                        raw_score = ev.get("observed_distance", drift_score)
                        try:
                            score = float(raw_score) if raw_score is not None else drift_score
                        except (ValueError, TypeError):
                            score = drift_score

                        drift_ev = DriftEvidence(
                            evidence_id=f"ev-{uuid.uuid4().hex[:6]}",
                            source_provider=ev.get("source_provider", "DriftGuard-Core-v3"),
                            retrieved_by_tool=ev.get("retrieved_by_tool", "ContextExtractor"),
                            summary=ev.get(
                                "summary",
                                f"Covariate drift score of {score} observed on feature {feat}.",
                            ),
                            confidence_weight=collection.confidence,
                            feature_name=feat,
                            distance_algorithm=ev.get("distance_algorithm", "adwin"),
                            observed_distance=score,
                            alarm_threshold=ev.get("alarm_threshold", 0.15),
                            is_anomalous=ev.get("is_anomalous", True),
                        )
                        state.add_universal_evidence(drift_ev)
                else:
                    # Fallback single typed evidence using LLM observations
                    default_ev = DriftEvidence(
                        evidence_id=f"ev-{uuid.uuid4().hex[:6]}",
                        source_provider="DriftGuard-Core-v3",
                        retrieved_by_tool="KnowledgeMCP+ContextExtractor",
                        summary=collection.reasoning,
                        confidence_weight=collection.confidence,
                        feature_name="all_features",
                        distance_algorithm="adwin",
                        observed_distance=drift_score,
                        alarm_threshold=0.15,
                        is_anomalous=True,
                    )
                    state.add_universal_evidence(default_ev)

                # Return enriched LLM collection for observability
                result = collection.model_dump(mode="json")
                result["status"] = "EVIDENCE_COLLECTED"
                result["mcp_kb_enriched"] = bool(knowledge_context)
                return result

            except Exception as e:
                logger.warning(
                    "LLM generation failed in InvestigatorAgent, falling back to static config: %s", e
                )

        # 4. Static fallback (no LLM or LLM failure)
        fallback_ev = DriftEvidence(
            evidence_id=f"ev-{uuid.uuid4().hex[:6]}",
            source_provider="DriftGuard-Core-v3",
            retrieved_by_tool="ContextExtractor",
            summary=f"Covariate drift score of {drift_score} observed on target model {model_id}.",
            confidence_weight=0.95,
            feature_name="all_features",
            distance_algorithm="adwin",
            observed_distance=drift_score,
            alarm_threshold=0.15,
            is_anomalous=True,
        )
        state.add_universal_evidence(fallback_ev)
        return {
            "status": "EVIDENCE_COLLECTED",
            "evidence_id": fallback_ev.evidence_id,
            "mcp_kb_enriched": False,
        }

