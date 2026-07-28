import json
import re
import datetime
import uuid
from typing import List, Dict, Any, Optional
from probe.storage.repository import EvidenceRepository
from probe.reasoning.artifacts import HypothesisArtifact
from .tools import SynthesisTools

class MalformedOutputError(Exception):
    pass

class UnsupportedEvidenceError(Exception):
    pass

class SynthesisOutputParser:
    """
    Validates raw JSON responses against strict schemas and ensures zero hallucinated evidence IDs.
    Converts valid JSON objects into immutable HypothesisArtifacts.
    """
    @classmethod
    def parse_and_validate(
        cls,
        raw_output: Any,
        investigation_id: str,
        repository: EvidenceRepository
    ) -> List[HypothesisArtifact]:
        # 1. Parse string to dict if needed
        data_dict: Optional[Dict[str, Any]] = None
        if isinstance(raw_output, dict):
            data_dict = raw_output
        elif isinstance(raw_output, str):
            cleaned = raw_output.strip()
            # Isolate outermost JSON object braces to tolerate conversational preambles from open-weight models
            start_idx = cleaned.find("{")
            end_idx = cleaned.rfind("}")
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                cleaned = cleaned[start_idx : end_idx + 1]
            try:
                data_dict = json.loads(cleaned)
            except json.JSONDecodeError as e:
                raise MalformedOutputError(f"[SynthesisOutputParser] Invalid JSON format: {str(e)}\nRaw: {cleaned[:200]}") from e
        else:
            raise MalformedOutputError(f"[SynthesisOutputParser] Unsupported output data type: {type(raw_output)}")

        if not data_dict or "hypotheses" not in data_dict:
            raise MalformedOutputError("[SynthesisOutputParser] Missing root attribute 'hypotheses' in JSON output.")

        items = data_dict.get("hypotheses", [])
        if not isinstance(items, list):
            raise MalformedOutputError("[SynthesisOutputParser] 'hypotheses' must be a JSON array.")

        if len(items) == 0:
            raise MalformedOutputError("[SynthesisOutputParser] Empty hypotheses array returned from synthesis engine.")

        artifacts: List[HypothesisArtifact] = []
        titles_seen = set()

        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                raise MalformedOutputError(f"[SynthesisOutputParser] Hypothesis at index {idx} is not an object.")

            title = str(item.get("title", "")).strip()
            desc = str(item.get("description", "")).strip()
            hypo_id = str(item.get("hypothesis_id", f"hyp-{idx+1}")).strip()
            ev_ids = item.get("supporting_evidence_ids", [])
            assumptions = item.get("assumptions", [])
            conf_inputs = item.get("confidence_inputs", {})
            trace = item.get("reasoning_trace", [])
            uncertainty = str(item.get("uncertainty", "LOW")).strip().upper()

            if not title:
                raise MalformedOutputError(f"[SynthesisOutputParser] Hypothesis at index {idx} has empty title.")
            if not desc:
                raise MalformedOutputError(f"[SynthesisOutputParser] Hypothesis '{title}' has empty description.")

            if title.lower() in titles_seen and title != "Insufficient Evidence":
                raise MalformedOutputError(f"[SynthesisOutputParser] Duplicate hypothesis title detected: '{title}'.")
            titles_seen.add(title.lower())

            if not isinstance(ev_ids, list):
                raise MalformedOutputError(f"[SynthesisOutputParser] supporting_evidence_ids must be a list for '{title}'.")

            # 2. Strict Evidence Reference Verification (No Hallucinations)
            is_valid, valid_ids, hallucinated = SynthesisTools.verify_evidence_ids_exist(ev_ids, repository)
            if not is_valid and title != "Insufficient Evidence":
                raise UnsupportedEvidenceError(
                    f"[SynthesisOutputParser] Hallucinated or unreachable evidence IDs referenced in '{title}': {hallucinated}"
                )

            # Check if claims are completely unsupported in normal explanations
            if len(valid_ids) == 0 and title != "Insufficient Evidence" and uncertainty != "INSUFFICIENT_EVIDENCE":
                raise UnsupportedEvidenceError(
                    f"[SynthesisOutputParser] Hypothesis '{title}' produces claims with zero valid supporting evidence IDs!"
                )

            now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
            art = HypothesisArtifact(
                artifact_id=f"art-synth-{uuid.uuid4().hex[:8]}",
                investigation_id=investigation_id,
                timestamp_utc=now_utc,
                producer_agent="CausalSynthesisAgent-v1",
                sha256_parent_evidence_ids=sorted(list(set(valid_ids))),
                hypothesis_id=hypo_id,
                root_cause_title=title,
                causal_chain_description=desc,
                supporting_evidence_ids=sorted(list(set(valid_ids))),
                initial_confidence=float(conf_inputs.get("plausibility_score", 0.70)) if isinstance(conf_inputs, dict) else 0.70,
                required_verification_queries=[],
                assumptions=assumptions if isinstance(assumptions, list) else [str(assumptions)],
                confidence_inputs=conf_inputs if isinstance(conf_inputs, dict) else {"raw": conf_inputs},
                reasoning_trace=trace if isinstance(trace, list) else [str(trace)],
                uncertainty=uncertainty
            )
            artifacts.append(art)

        # 3. Rank competing hypotheses by evidence count and plausibility
        def rank_key(a: HypothesisArtifact):
            if a.root_cause_title == "Insufficient Evidence":
                return -1.0
            return len(a.supporting_evidence_ids) * 10.0 + a.initial_confidence

        artifacts.sort(key=rank_key, reverse=True)
        return artifacts
