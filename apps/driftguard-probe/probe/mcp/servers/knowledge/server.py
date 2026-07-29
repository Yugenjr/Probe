"""KnowledgeServer — MCP server for knowledge base operations.

Owns the 'knowledge' namespace. Delegates all storage I/O to KnowledgeRepository.
Uses ToolExecutor to wrap each tool call with timing and exception safety.

Adding a new knowledge tool:
  1. Write the tool class in tools.py
  2. Import and register it in _tools below
  Done.
"""
import logging
from typing import Any, Dict, List

from ...server import BaseMCPServer
from ...tools.tool_executor import ToolExecutor
from ...types import ToolResult, ToolDefinition
from .repository import KnowledgeRepository
from .tools import (
    SearchDocumentsTool,
    GetDocumentTool,
    ListDocumentsTool,
    SearchInvestigationsTool,
    SearchRunbooksTool,
)

logger = logging.getLogger(__name__)


class KnowledgeServer(BaseMCPServer):
    """MCP server exposing knowledge base capabilities.

    The server is the boundary between the MCP layer and knowledge storage.
    It knows about tools and routing — nothing about files, JSON, or paths.
    All of that lives in KnowledgeRepository.

    Future migration path:
      KnowledgeServer(repository=PostgresKnowledgeRepository(conn_str))
      → No other changes required.
    """

    def __init__(
        self,
        repository: KnowledgeRepository = None,
        base_dir: str = "storage/knowledge",
    ) -> None:
        self._repo = repository or KnowledgeRepository(base_dir=base_dir)
        self._executor = ToolExecutor()

        self._tools = {
            "search_documents": SearchDocumentsTool(self._repo),
            "get_document": GetDocumentTool(self._repo),
            "list_documents": ListDocumentsTool(self._repo),
            "search_investigations": SearchInvestigationsTool(self._repo),
            "search_runbooks": SearchRunbooksTool(self._repo),
        }
        logger.info(
            "[KnowledgeServer] Initialized with %d tools: %s",
            len(self._tools),
            list(self._tools.keys()),
        )

    @property
    def name(self) -> str:
        return "knowledge"

    def get_tools(self) -> List[ToolDefinition]:
        """Return tool definitions for registry discovery."""
        return [t.definition for t in self._tools.values()]

    async def handle_tool_call(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> ToolResult:
        """Dispatch a tool call to the appropriate handler."""
        tool = self._tools.get(tool_name)
        if tool is None:
            known = list(self._tools.keys())
            msg = f"Tool '{tool_name}' not found in KnowledgeServer. Known: {known}"
            logger.warning("[KnowledgeServer] %s", msg)
            return ToolResult(success=False, content="", error=msg)

        logger.debug(
            "[KnowledgeServer] Dispatching tool=%r args=%s",
            tool_name, list(arguments.keys())
        )
        return await self._executor.run(tool, arguments)
