"""Reusable DriftGuard SDK Client with tenacity retry logic, timeout management, and custom exception mapping."""
import logging
import re
from typing import Any, Dict, List, Optional
import httpx
import tenacity

from probe.adapters.driftguard.exceptions import DriftGuardError, DriftGuardAPIError, DriftGuardConnectionError

logger = logging.getLogger(__name__)


class DriftGuardAuthenticationError(DriftGuardAPIError):
    """401 or 403 authorization failures."""
    pass


class DriftGuardNotFoundError(DriftGuardAPIError):
    """404 resource not found errors."""
    pass


class DriftGuardServerError(DriftGuardAPIError):
    """500 server errors from SDK."""
    pass


def is_retryable_exception(exception: Exception) -> bool:
    """Filter to determine if tenacity should retry the request."""
    if isinstance(exception, (httpx.ConnectError, httpx.TimeoutException, DriftGuardServerError, DriftGuardConnectionError)):
        return True
    return False


class DriftGuardClient:
    """Enterprise REST client for authenticating and fetching data from the DriftGuard SDK."""

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        
        self._sync_client = httpx.Client(base_url=self.base_url, timeout=self.timeout)
        self._async_client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)

    def _get_headers(self) -> Dict[str, str]:
        """Generate headers with auth keys safely attached."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _handle_response(self, response: httpx.Response) -> Any:
        """Evaluate status codes and raise domain-specific clean exceptions."""
        if response.status_code in (401, 403):
            raise DriftGuardAuthenticationError(response.status_code, f"Unauthorized access: {response.text}")
        elif response.status_code == 404:
            raise DriftGuardNotFoundError(response.status_code, f"Resource not found: {response.text}")
        elif response.status_code >= 500:
            raise DriftGuardServerError(response.status_code, f"DriftGuard server reported an internal error: {response.text}")

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise DriftGuardError(f"HTTP Error {response.status_code}: {e}") from e

        if "application/json" in response.headers.get("content-type", ""):
            return response.json()
        return response.text

    def _execute_request(self, method: str, path: str, **kwargs: Any) -> Any:
        """Synchronously execute HTTP requests with retry policies."""
        headers = self._get_headers()
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers

        try:
            for attempt in tenacity.Retrying(
                stop=tenacity.stop_after_attempt(self.max_retries),
                wait=tenacity.wait_exponential(multiplier=1, min=1, max=5),
                retry=tenacity.retry_if_exception(is_retryable_exception),
                reraise=True
            ):
                with attempt:
                    try:
                        resp = self._sync_client.request(method, path, **kwargs)
                        if resp.status_code >= 500:
                            raise DriftGuardServerError(resp.status_code, f"Server Error {resp.status_code}")
                        return self._handle_response(resp)
                    except (httpx.ConnectError, httpx.TimeoutException) as exc:
                        raise DriftGuardConnectionError(f"Connection failure calling SDK path {path}: {exc}") from exc
        except Exception as e:
            if isinstance(e, DriftGuardError):
                raise
            raise DriftGuardError(f"DriftGuard SDK call failed: {e}") from e

    async def _execute_request_async(self, method: str, path: str, **kwargs: Any) -> Any:
        """Asynchronously execute HTTP requests with retry policies."""
        headers = self._get_headers()
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers

        try:
            async for attempt in tenacity.AsyncRetrying(
                stop=tenacity.stop_after_attempt(self.max_retries),
                wait=tenacity.wait_exponential(multiplier=1, min=1, max=5),
                retry=tenacity.retry_if_exception(is_retryable_exception),
                reraise=True
            ):
                with attempt:
                    try:
                        resp = await self._async_client.request(method, path, **kwargs)
                        if resp.status_code >= 500:
                            raise DriftGuardServerError(resp.status_code, f"Server Error {resp.status_code}")
                        return self._handle_response(resp)
                    except (httpx.ConnectError, httpx.TimeoutException) as exc:
                        raise DriftGuardConnectionError(f"Connection failure calling SDK path {path}: {exc}") from exc
        except Exception as e:
            if isinstance(e, DriftGuardError):
                raise
            raise DriftGuardError(f"DriftGuard SDK call failed: {e}") from e

    # --- Synchronous SDK API endpoints ---
    def get_model_details(self, model_id: str) -> Dict[str, Any]:
        return self._execute_request("GET", f"/models/{model_id}")

    def get_model_versions(self, model_id: str) -> List[Dict[str, Any]]:
        return self._execute_request("GET", f"/models/{model_id}/versions")

    def get_drift_history(self, model_id: str) -> List[Dict[str, Any]]:
        return self._execute_request("GET", f"/drift/{model_id}")

    def get_audit_logs(self, model_id: str) -> List[Dict[str, Any]]:
        return self._execute_request("GET", f"/audit/{model_id}")

    def get_retraining_history(self, model_id: str) -> List[Dict[str, Any]]:
        return self._execute_request("GET", f"/retraining/history/{model_id}")

    def get_metrics(self) -> str:
        return self._execute_request("GET", "/metrics")

    def trigger_retraining(self, model_id: str, drift_score: float = 0.15) -> Dict[str, Any]:
        return self._execute_request("POST", f"/retrain/{model_id}", json={"drift_score": drift_score})

    # --- Asynchronous SDK API endpoints ---
    async def aget_model_details(self, model_id: str) -> Dict[str, Any]:
        return await self._execute_request_async("GET", f"/models/{model_id}")

    async def aget_model_versions(self, model_id: str) -> List[Dict[str, Any]]:
        return await self._execute_request_async("GET", f"/models/{model_id}/versions")

    async def aget_drift_history(self, model_id: str) -> List[Dict[str, Any]]:
        return await self._execute_request_async("GET", f"/drift/{model_id}")

    async def aget_audit_logs(self, model_id: str) -> List[Dict[str, Any]]:
        return await self._execute_request_async("GET", f"/audit/{model_id}")

    async def aget_retraining_history(self, model_id: str) -> List[Dict[str, Any]]:
        return await self._execute_request_async("GET", f"/retraining/history/{model_id}")

    async def aget_metrics(self) -> str:
        return await self._execute_request_async("GET", "/metrics")

    async def atrigger_retraining(self, model_id: str, drift_score: float = 0.15) -> Dict[str, Any]:
        return await self._execute_request_async("POST", f"/retrain/{model_id}", json={"drift_score": drift_score})

    def close(self):
        self._sync_client.close()

    async def aclose(self):
        await self._async_client.aclose()
