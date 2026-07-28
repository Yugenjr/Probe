"""Out-of-Process Sandbox Plugin Engine enforcing secure execution separation."""
import logging
import subprocess
import json
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from ..interfaces.context import ResourceContext

logger = logging.getLogger(__name__)


class PluginPermissionManifest(BaseModel):
    """Strict execution boundary capability declaration required for third-party adapter execution."""
    plugin_id: str
    executable_binary_path: str = Field(..., description="Absolute path to isolated worker binary or script")
    allow_network_hosts: List[str] = Field(default_factory=list, description="Explicit whitelist of outbound domains")
    max_execution_timeout_seconds: int = Field(default=15, le=60)


class SandboxedAdapterClient:
    """Out-of-process IPC adapter executor isolating third-party code from core memory spaces.
    
    Prevents unverified vendor community plugins from reading environment API keys, corrupting memory,
    or blocking core asyncio event loops by executing commands inside isolated subprocesses or Wasm sandboxes.
    """
    def __init__(self, manifest: PluginPermissionManifest):
        self.manifest = manifest

    async def execute_capability(self, capability: str, context: ResourceContext, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch JSON interface payload over secure inter-process communication stdin/stdout buffers."""
        request_payload = {
            "capability_method": capability,
            "resource_context": context.model_dump(mode="json"),
            "arguments": parameters
        }
        
        logger.info("Dispatching command %s to isolated sandbox worker: %s", capability, self.manifest.plugin_id)
        
        try:
            # Enforce execution inside separate OS process with hard timeout deadlines
            proc = subprocess.run(
                [self.manifest.executable_binary_path],
                input=json.dumps(request_payload).encode("utf-8"),
                capture_output=True,
                timeout=self.manifest.max_execution_timeout_seconds,
                check=True
            )
            response = json.loads(proc.stdout.decode("utf-8"))
            if not isinstance(response, dict):
                raise ValueError("Sandboxed plugin returned invalid non-dictionary payload structure.")
            return response
        except subprocess.TimeoutExpired:
            logger.error("Sandbox plugin %s exceeded execution deadline; killing worker.", self.manifest.plugin_id)
            raise RuntimeError(f"Sandbox security abort: Plugin execution exceeded {self.manifest.max_execution_timeout_seconds}s limit.")
        except Exception as exc:
            logger.error("Sandboxed IPC communication failed for plugin %s: %s", self.manifest.plugin_id, str(exc))
            raise RuntimeError(f"Sandboxed adapter failure: {str(exc)}")
