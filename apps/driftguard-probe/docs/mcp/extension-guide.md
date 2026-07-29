# MCP Extension Guide — Adding a New Server

This guide explains exactly what is required to add a new MCP server (e.g., GitHub, Prometheus, MLflow).

## What You Need to Write

### 1. Server class (`BaseMCPServer`)

```python
# probe/mcp/servers/github/server.py
from probe.mcp.server import BaseMCPServer
from probe.mcp.types import ToolResult, ToolDefinition

class GitHubServer(BaseMCPServer):
    @property
    def name(self) -> str:
        return "github"   # This becomes the namespace: registry.execute(server="github", ...)

    def get_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition(
                name="search_code",
                description="Search GitHub repositories for code patterns",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "repo": {"type": "string"},
                    },
                    "required": ["query"]
                },
                server="github"
            )
        ]

    async def handle_tool_call(self, tool_name: str, arguments: dict) -> ToolResult:
        if tool_name == "search_code":
            # Call GitHub API, return ToolResult
            ...
        return ToolResult(success=False, content="", error=f"Unknown tool: {tool_name}")
```

### 2. Repository (optional but recommended)

```python
# probe/mcp/servers/github/repository.py
class GitHubRepository:
    """All GitHub API I/O lives here. Server stays clean."""
    def search_code(self, query: str, repo: str) -> list[dict]: ...
```

### 3. Tools file

```python
# probe/mcp/servers/github/tools.py
class SearchCodeTool(BaseMCPTool):
    def __init__(self, repo: GitHubRepository): ...
    @property
    def definition(self) -> ToolDefinition: ...
    async def execute(self, query: str, repo: str = "", **kwargs) -> ToolResult: ...
```

## What You Register (startup only)

```python
# probe/api/main.py  — inside lifespan()
mcp_registry.register(GitHubServer())
```

## What You Do NOT Touch

- `ToolGateway` — no changes
- `ServerRegistry` — no changes  
- `InvestigatorAgent` — no changes
- Any other agent — no changes
- `AgentExecutor` — no changes

## Naming Conventions

| Component | Pattern | Example |
|-----------|---------|---------|
| Server class | `{Name}Server` | `GitHubServer`, `PrometheusServer` |
| Server name | lowercase | `"github"`, `"prometheus"` |
| Tool names | `snake_case` | `"search_code"`, `"get_metric"` |
| Repository | `{Name}Repository` | `GitHubRepository` |

## File Layout for a New Server

```
probe/mcp/servers/github/
    __init__.py
    server.py       ← GitHubServer(BaseMCPServer)
    repository.py   ← GitHubRepository (API calls here)
    tools.py        ← All GitHub tools in one file
```

## Future Transport Support

For servers running as external processes (stdio MCP protocol):
```python
# When HttpTransport is implemented:
mcp_registry.register(
    GitHubServer(),
    transport=HttpTransport("http://github-mcp-server:3000")
)
```

The `ServerRegistry.register()` signature will be extended to accept an explicit transport. The rest of the stack stays identical.
