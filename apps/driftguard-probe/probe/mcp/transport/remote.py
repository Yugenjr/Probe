"""HTTP and Process transports for remote MCP servers."""
import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional
import httpx

from ..types import ToolResult, ToolDefinition
from ..server import BaseMCPServer
from ..jsonrpc import JSONRPCRequest, JSONRPCResponse

logger = logging.getLogger(__name__)


class HttpTransport:
    """Transport communicating with remote HTTP MCP servers via JSON-RPC.

    Discovers tools dynamically and routes execute requests.
    """

    def __init__(self, server_name: str, url: str, headers: Optional[Dict[str, str]] = None) -> None:
        self._server_name = server_name
        self._url = url
        self._headers = headers or {}
        self._tools_cache: List[ToolDefinition] = []
        self._last_health_check_status = False
        self._last_latency_ms = 0

    @property
    def server_name(self) -> str:
        return self._server_name

    @property
    def last_latency_ms(self) -> int:
        return self._last_latency_ms

    @property
    def connected(self) -> bool:
        return self._last_health_check_status

    async def list_tools(self) -> List[ToolDefinition]:
        """Discovers tools dynamically via json-rpc 'tools/list'."""
        start = time.perf_counter()
        req = JSONRPCRequest(method="tools/list", id=1)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    self._url,
                    json=req.model_dump(),
                    headers={"Content-Type": "application/json", **self._headers}
                )
                self._last_latency_ms = int((time.perf_counter() - start) * 1000)
                if resp.status_code == 200:
                    data = resp.json()
                    res_body = JSONRPCResponse.model_validate(data)
                    if res_body.result and "tools" in res_body.result:
                        tools = []
                        for t in res_body.result["tools"]:
                            tools.append(
                                ToolDefinition(
                                    name=t["name"],
                                    description=t.get("description", ""),
                                    parameters=t.get("inputSchema", {}),
                                    server=self._server_name
                                )
                            )
                        self._tools_cache = tools
                        self._last_health_check_status = True
                        return tools
            self._last_health_check_status = False
            return self._tools_cache
        except Exception as e:
            logger.error("[HttpTransport] Failed list_tools for %s: %s", self._server_name, e)
            self._last_health_check_status = False
            return self._tools_cache

    async def call(self, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Call a tool remotely via 'tools/call'."""
        start = time.perf_counter()
        req = JSONRPCRequest(
            method="tools/call",
            params={"name": tool_name, "arguments": arguments},
            id=2
        )
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    self._url,
                    json=req.model_dump(),
                    headers={"Content-Type": "application/json", **self._headers}
                )
                elapsed = int((time.perf_counter() - start) * 1000)
                self._last_latency_ms = elapsed
                if resp.status_code == 200:
                    data = resp.json()
                    res_body = JSONRPCResponse.model_validate(data)
                    if res_body.error:
                        return ToolResult(
                            success=False,
                            content="",
                            error=res_body.error.get("message", "Error from remote server"),
                            execution_time_ms=elapsed
                        )
                    if res_body.result and "content" in res_body.result:
                        # Extract first text content item
                        text_items = [
                            c.get("text", "")
                            for c in res_body.result["content"]
                            if c.get("type") == "text"
                        ]
                        text = "\n".join(text_items)
                        return ToolResult(
                            success=True,
                            content=text,
                            artifacts=res_body.result.get("content", []),
                            execution_time_ms=elapsed
                        )
            return ToolResult(
                success=False,
                content="",
                error=f"HTTP status {resp.status_code} received from remote server.",
                execution_time_ms=int((time.perf_counter() - start) * 1000)
            )
        except Exception as e:
            logger.error("[HttpTransport] Call error: %s", e)
            return ToolResult(
                success=False,
                content="",
                error=f"Transport connection error: {e}",
                execution_time_ms=int((time.perf_counter() - start) * 1000)
            )


class ProcessTransport:
    """Transport starting a subprocess and communicating via JSON-RPC stdio.

    Example: MLflow MCP started via 'uv run mlflow mcp run'.
    """

    def __init__(
        self,
        server_name: str,
        command: str,
        args: List[str],
        env: Optional[Dict[str, str]] = None
    ) -> None:
        self._server_name = server_name
        self._command = command
        self._args = args
        self._env = env or {}
        self._process: Optional[asyncio.subprocess.Process] = None
        self._tools_cache: List[ToolDefinition] = []
        self._last_latency_ms = 0
        self._connected = False
        self._lock = asyncio.Lock()

    @property
    def server_name(self) -> str:
        return self._server_name

    @property
    def last_latency_ms(self) -> int:
        return self._last_latency_ms

    @property
    def connected(self) -> bool:
        return self._connected

    async def _ensure_started(self) -> None:
        if self._process is not None and self._process.returncode is None:
            return

        try:
            logger.info(
                "[ProcessTransport] Starting process for %s: %s %s",
                self._server_name, self._command, self._args
            )
            # Find command in path if on Windows
            import shutil
            executable = shutil.which(self._command) or self._command

            self._process = await asyncio.create_subprocess_exec(
                executable,
                *self._args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
                env=self._env
            )
            self._connected = True
        except Exception as e:
            logger.error("[ProcessTransport] Process start failed: %s", e)
            self._connected = False
            raise e

    async def list_tools(self) -> List[ToolDefinition]:
        """Send tools/list request to subprocess."""
        async with self._lock:
            start = time.perf_counter()
            try:
                await self._ensure_started()
                if not self._process or not self._process.stdin or not self._process.stdout:
                    return []

                req = JSONRPCRequest(method="tools/list", id=1)
                payload = json.dumps(req.model_dump()) + "\n"
                self._process.stdin.write(payload.encode("utf-8"))
                await self._process.stdin.drain()

                line = await self._process.stdout.readline()
                self._last_latency_ms = int((time.perf_counter() - start) * 1000)
                if line:
                    data = json.loads(line.decode("utf-8").strip())
                    res_body = JSONRPCResponse.model_validate(data)
                    if res_body.result and "tools" in res_body.result:
                        tools = []
                        for t in res_body.result["tools"]:
                            tools.append(
                                ToolDefinition(
                                    name=t["name"],
                                    description=t.get("description", ""),
                                    parameters=t.get("inputSchema", {}),
                                    server=self._server_name
                                )
                            )
                        self._tools_cache = tools
                        return tools
            except Exception as e:
                logger.error("[ProcessTransport] list_tools error: %s", e)
                self._connected = False
            return self._tools_cache

    async def call(self, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Send tools/call request to subprocess."""
        async with self._lock:
            start = time.perf_counter()
            try:
                await self._ensure_started()
                if not self._process or not self._process.stdin or not self._process.stdout:
                    return ToolResult(
                        success=False, content="", error="Process stdio channel closed."
                    )

                req = JSONRPCRequest(
                    method="tools/call",
                    params={"name": tool_name, "arguments": arguments},
                    id=2
                )
                payload = json.dumps(req.model_dump()) + "\n"
                self._process.stdin.write(payload.encode("utf-8"))
                await self._process.stdin.drain()

                line = await self._process.stdout.readline()
                elapsed = int((time.perf_counter() - start) * 1000)
                self._last_latency_ms = elapsed
                if line:
                    data = json.loads(line.decode("utf-8").strip())
                    res_body = JSONRPCResponse.model_validate(data)
                    if res_body.error:
                        return ToolResult(
                            success=False,
                            content="",
                            error=res_body.error.get("message", "Error from process server"),
                            execution_time_ms=elapsed
                        )
                    if res_body.result and "content" in res_body.result:
                        text_items = [
                            c.get("text", "")
                            for c in res_body.result["content"]
                            if c.get("type") == "text"
                        ]
                        text = "\n".join(text_items)
                        return ToolResult(
                            success=True,
                            content=text,
                            artifacts=res_body.result.get("content", []),
                            execution_time_ms=elapsed
                        )
            except Exception as e:
                logger.error("[ProcessTransport] call error: %s", e)
                self._connected = False
                return ToolResult(
                    success=False,
                    content="",
                    error=f"Process execution error: {e}",
                    execution_time_ms=int((time.perf_counter() - start) * 1000)
                )

            return ToolResult(
                success=False,
                content="",
                error="Empty response from process stdout.",
                execution_time_ms=int((time.perf_counter() - start) * 1000)
            )
