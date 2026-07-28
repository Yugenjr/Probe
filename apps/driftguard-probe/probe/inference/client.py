import time
import urllib.parse
from typing import Type, Any, Dict, Optional, TypeVar, Callable
from pydantic import BaseModel
from probe.storage.repository import EvidenceRepository
from .config import InferenceConfig
from .exceptions import (
    InferenceException, InferenceTimeoutError, InferenceBackendError,
    MalformedResponseError, SchemaValidationError, EvidenceHallucinationError
)
from .models import InferenceResult
from .parser import ResponseParser
from .validator import SchemaValidator
from .telemetry import TelemetryCollector, InferenceTelemetryRecord

T = TypeVar("T", bound=BaseModel)

class InferenceClient:
    """
    Production Probe Inference Engine Client.
    The ONLY component allowed to communicate with AI model backends.
    Responsibilities: send requests, receive structured responses, parse JSON, validate schemas,
    retry transient failures with exponential backoff, record operational telemetry, and return typed Pydantic objects.
    """
    def __init__(
        self,
        config: Optional[InferenceConfig] = None,
        telemetry_collector: Optional[TelemetryCollector] = None,
        transport_override: Optional[Callable[[Dict[str, Any], float], str]] = None
    ):
        self._config = config or InferenceConfig()
        self._telemetry = telemetry_collector or TelemetryCollector()
        self._transport = transport_override  # Permits deterministic offline testing without network binding

    @property
    def config(self) -> InferenceConfig:
        return self._config

    @property
    def telemetry(self) -> TelemetryCollector:
        return self._telemetry

    def generate(
        self,
        prompt_bundle: Dict[str, str],
        target_schema: Type[T],
        evidence_repository: Optional[EvidenceRepository] = None
    ) -> InferenceResult[T]:
        """
        Executes generation with exponential backoff retries, schema validation, and secure operational logging.
        Reasoning modules receive ONLY the verified typed InferenceResult[T].
        """
        system_instr = prompt_bundle.get("system_instructions", "")
        user_payload = prompt_bundle.get("user_payload", "")
        
        request_body = {
            "model": self._config.model_identifier,
            "temperature": self._config.temperature,
            "top_p": self._config.top_p,
            "max_tokens": self._config.max_tokens,
            "seed": self._config.seed,
            "messages": [
                {"role": "system", "content": system_instr},
                {"role": "user", "content": user_payload}
            ]
        }

        parsed_url = urllib.parse.urlparse(self._config.endpoint)
        endpoint_host = parsed_url.hostname or self._config.endpoint

        attempt = 0
        last_exception: Optional[Exception] = None

        while attempt < self._config.max_retries:
            attempt += 1
            start_time_ms = time.perf_counter() * 1000.0
            
            try:
                raw_text_or_dict = self._dispatch_request(request_body)
                parsed_dict = ResponseParser.parse_to_dict(raw_text_or_dict)
                validated_artifact = SchemaValidator.validate_and_instantiate(
                    payload_dict=parsed_dict,
                    target_model=target_schema,
                    repository=evidence_repository
                )

                end_time_ms = time.perf_counter() * 1000.0
                latency_ms = round(end_time_ms - start_time_ms, 2)
                response_size = len(str(raw_text_or_dict))
                approx_tokens = max(10, int(response_size / 4))

                # Log successful operational telemetry (No secrets or payloads)
                record = InferenceTelemetryRecord(
                    model_identifier=self._config.model_identifier,
                    request_duration_ms=latency_ms,
                    token_usage_approx=approx_tokens,
                    response_bytes_size=response_size,
                    retry_count=attempt - 1,
                    success=True,
                    failure_error_type=None,
                    endpoint_hostname=endpoint_host
                )
                self._telemetry.log_record(record)

                return InferenceResult(
                    artifact=validated_artifact,
                    model_identifier=self._config.model_identifier,
                    latency_ms=latency_ms,
                    retry_count=attempt - 1,
                    token_usage_approx=approx_tokens
                )

            except (
                InferenceTimeoutError,
                InferenceBackendError,
                MalformedResponseError,
                SchemaValidationError,
                EvidenceHallucinationError
            ) as e:
                last_exception = e
                end_time_ms = time.perf_counter() * 1000.0
                duration_ms = round(end_time_ms - start_time_ms, 2)
                
                # If attempt < max_retries, apply exponential backoff
                if attempt < self._config.max_retries:
                    backoff_delay = self._config.retry_base_delay_seconds * (2 ** (attempt - 1))
                    time.sleep(backoff_delay)
                else:
                    # Log failure operational telemetry upon final attempt exhaustion
                    fail_record = InferenceTelemetryRecord(
                        model_identifier=self._config.model_identifier,
                        request_duration_ms=duration_ms,
                        token_usage_approx=0,
                        response_bytes_size=0,
                        retry_count=attempt,
                        success=False,
                        failure_error_type=type(e).__name__,
                        endpoint_hostname=endpoint_host
                    )
                    self._telemetry.log_record(fail_record)

            except Exception as e:
                last_exception = InferenceBackendError(f"[InferenceClient] Uncaught backend failure: {str(e)}")
                break

        raise InferenceBackendError(
            f"[InferenceClient] Generation failed after exhausting {attempt} retry attempts. Last error: {str(last_exception)}"
        ) from last_exception

    def _dispatch_request(self, request_body: Dict[str, Any]) -> Any:
        if self._transport:
            try:
                return self._transport(request_body, self._config.timeout_seconds)
            except TimeoutError as te:
                raise InferenceTimeoutError(f"Inference timeout after {self._config.timeout_seconds}s") from te
            except Exception as e:
                if isinstance(e, (InferenceTimeoutError, InferenceBackendError)):
                    raise e
                raise InferenceBackendError(f"Inference transport execution failed: {str(e)}") from e

        # Standard production HTTP network dispatch via urllib / requests fallback
        import urllib.request
        import urllib.error
        req_data = json.dumps(request_body).encode("utf-8")
        req = urllib.request.Request(
            self._config.endpoint,
            data=req_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._config.authentication_token}"
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=self._config.timeout_seconds) as resp:
                resp_data = resp.read().decode("utf-8")
                resp_json = json.loads(resp_data)
                # Parse OpenAI compatible completion content
                choices = resp_json.get("choices", [])
                if choices and "message" in choices[0]:
                    return choices[0]["message"].get("content", "")
                return resp_data
        except urllib.error.HTTPError as he:
            raise InferenceBackendError(f"HTTP {he.code}: {he.reason}") from he
        except urllib.error.URLError as ue:
            if "timeout" in str(ue.reason).lower():
                raise InferenceTimeoutError("Connection timeout exceeded.") from ue
            raise InferenceBackendError(f"Network routing failure: {ue.reason}") from ue
        except TimeoutError as te2:
            raise InferenceTimeoutError("Socket read timeout exceeded.") from te2
