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

    async def _read_mcp_message(self, timeout: float = 30.0) -> Optional[Dict]:
        """Read one MCP message from stdout.

        Handles two wire formats:
        1. Content-Length framed (used by @modelcontextprotocol/server-github):
              Content-Length: <N>\\r\\n\\r\\n<JSON body of N bytes>
        2. Plain newline-delimited JSON (used by simpler servers like MLflow).
        
        Skips any extraneous non-JSON lines (e.g. from npx or warnings).
        """
        if not self._process or not self._process.stdout:
            return None

        async def _read() -> Optional[Dict]:
            while True:
                # Read line by line until we find a valid message
                first_line = await self._process.stdout.readline()
                if not first_line:
                    return None
                first_line_str = first_line.decode("utf-8", errors="replace").strip()

                if not first_line_str:
                    continue

                logger.debug("[ProcessTransport][%s] Read line: %s", self._server_name, repr(first_line_str[:500]))

                # --- Content-Length framing ---
                if first_line_str.lower().startswith("content-length:"):
                    try:
                        length = int(first_line_str.split(":", 1)[1].strip())
                    except ValueError:
                        continue
                    # Consume blank separator line(s) (\r\n)
                    while True:
                        sep = await self._process.stdout.readline()
                        if not sep or sep.strip() == b"":
                            break
                    # Read exact body
                    body = await self._process.stdout.readexactly(length)
                    try:
                        return json.loads(body.decode("utf-8"))
                    except json.JSONDecodeError:
                        continue

                # --- Plain newline JSON ---
                if first_line_str.startswith("{"):
                    try:
                        return json.loads(first_line_str)
                    except json.JSONDecodeError:
                        pass
                
                # If we get here, it was a non-JSON log line. Keep looping.

        try:
            return await asyncio.wait_for(_read(), timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning("[ProcessTransport] _read_mcp_message timed out for '%s'", self._server_name)
            return None
        except Exception as e:
            logger.warning("[ProcessTransport] _read_mcp_message failed for '%s': %s", self._server_name, e)
            return None

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
            import os
            import sys
            import shutil

            # Search order:
            # 1. System PATH (shutil.which)
            # 2. Scripts/ dir of the currently-running Python interpreter's venv
            # 3. Fall back to bare command name and let the OS raise a clear error
            executable = shutil.which(self._command)
            if executable is None:
                venv_scripts = os.path.join(
                    os.path.dirname(sys.executable), ""
                )
                candidate = os.path.join(venv_scripts, self._command)
                # On Windows, also try with .exe / .cmd suffixes
                for suffix in ("", ".exe", ".cmd", ".bat"):
                    if os.path.isfile(candidate + suffix):
                        executable = candidate + suffix
                        break
                else:
                    executable = self._command  # let OS error surface naturally

            logger.info(
                "[ProcessTransport] Resolved command '%s' -> '%s'",
                self._command, executable
            )

            # Merge parent os.environ with YAML-supplied env vars so that
            # subprocess inherits PATH, APPDATA, NODE_PATH etc. and the
            # custom vars (e.g. GITHUB_PERSONAL_ACCESS_TOKEN) still override.
            merged_env = {**os.environ, **self._env}

            if executable.lower().endswith(".cmd") or executable.lower().endswith(".bat"):
                # Use create_subprocess_shell for .cmd files to ensure stdio piping works
                import subprocess
                cmd_line = f'"{executable}" ' + ' '.join(f'"{a}"' for a in self._args)
                self._process = await asyncio.create_subprocess_shell(
                    cmd_line,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=merged_env,
                    limit=10485760
                )
            else:
                self._process = await asyncio.create_subprocess_exec(
                    executable,
                    *self._args,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=merged_env,
                    limit=10485760
                )

            # ── MCP initialize handshake ──────────────────────────────────
            # Step 1: send initialize request
            init_req = JSONRPCRequest(
                method="initialize",
                params={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "driftguard-probe", "version": "0.1.0"}
                },
                id=0
            )
            self._process.stdin.write((json.dumps(init_req.model_dump()) + "\r\n").encode())
            await self._process.stdin.drain()

            # Step 2: read initialize response via format-aware reader (180s for first npx/uv download)
            await self._read_mcp_message(timeout=180.0)

            # Step 3: send notifications/initialized (required by MCP spec before tools/list)
            notif = {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
            self._process.stdin.write((json.dumps(notif) + "\r\n").encode())
            await self._process.stdin.drain()

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
                self._process.stdin.write((json.dumps(req.model_dump()) + "\r\n").encode())
                await self._process.stdin.drain()

                # Skip any notifications (no "id") — GitHub MCP sends log
                # notifications before the actual tools/list response.
                # Allow 180s: GitHub MCP validates PAT via API on first call.
                data = None
                deadline = time.perf_counter() + 180.0
                while time.perf_counter() < deadline:
                    remaining = deadline - time.perf_counter()
                    msg = await self._read_mcp_message(timeout=max(remaining, 1.0))
                    if msg is None:
                        break
                    # Notifications have no "id" field — skip them
                    if "id" in msg:
                        data = msg
                        break

                self._last_latency_ms = int((time.perf_counter() - start) * 1000)
                if data:
                    res_body = JSONRPCResponse.model_validate(data)
                    if res_body.result and "tools" in res_body.result:
                        tools = [
                            ToolDefinition(
                                name=t["name"],
                                description=t.get("description", ""),
                                parameters=t.get("inputSchema", {}),
                                server=self._server_name
                            )
                            for t in res_body.result["tools"]
                        ]
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
                self._process.stdin.write((json.dumps(req.model_dump()) + "\r\n").encode())
                await self._process.stdin.drain()

                data = await self._read_mcp_message(timeout=30.0)
                elapsed = int((time.perf_counter() - start) * 1000)
                self._last_latency_ms = elapsed
                if data:
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
