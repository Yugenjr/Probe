"""OpenTelemetry distributed tracer and logger bootstrapping with defensive fallback."""
import logging
from typing import Any, Optional
from .config import Settings

logger = logging.getLogger(__name__)

try:
    from opentelemetry import trace as otel_trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    HAS_OTEL = True
except (ImportError, Exception):
    HAS_OTEL = False


class DummyTracer:
    """Fallback dummy tracer instance when OpenTelemetry dependencies are uninstalled."""
    def start_as_current_span(self, name: str, *args, **kwargs):
        from contextlib import nullcontext
        return nullcontext()


def initialize_telemetry(settings: Settings) -> None:
    """Initialize OpenTelemetry tracer providers and exporter targets if available."""
    if not settings.enable_telemetry or not HAS_OTEL:
        logger.info("OpenTelemetry instrumentation disabled or framework uninstalled; utilizing dummy tracer.")
        return

    try:
        provider = TracerProvider()
        processor = BatchSpanProcessor(ConsoleSpanExporter())
        provider.add_span_processor(processor)
        otel_trace.set_tracer_provider(provider)
        logger.info("OpenTelemetry Tracer initialized for service: %s", settings.telemetry_service_name)
    except Exception as exc:
        logger.warning("Failed to initialize OpenTelemetry tracer: %s", str(exc))


def get_tracer(module_name: str) -> Any:
    """Acquire standard distributed tracer instance or fallback dummy tracer."""
    if HAS_OTEL:
        try:
            return otel_trace.get_tracer(module_name)
        except Exception:
            pass
    return DummyTracer()
