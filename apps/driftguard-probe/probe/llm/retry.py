"""Tenacity retry logic for resilient LLM inference calls."""
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


def log_retry_attempt(retry_state) -> None:
    """Callback function logging retry occurrences during inference failures."""
    logger.warning("Retrying LLM call after error (attempt %s): %s", retry_state.attempt_number, retry_state.outcome)


llm_retry_policy = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((Exception,)),
    before_sleep=log_retry_attempt,
)
# TODO: Implementation pending for fine-grained HTTP rate limit vs formatting error discrimination
