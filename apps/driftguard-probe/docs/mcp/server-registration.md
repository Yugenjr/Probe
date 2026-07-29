# Server Registration Guide

## How Registration Works

```python
# probe/api/main.py — lifespan startup

registry = ServerRegistry()

# Register Knowledge server (in-process, filesystem-backed)
registry.register(KnowledgeServer())

# Future registrations — one line each, no other changes
# registry.register(GitHubServer())
# registry.register(PrometheusServer(endpoint="http://prometheus:9090"))
# registry.register(MLflowServer(tracking_uri="http://mlflow:5000"))

container.tool_gateway = ToolGateway(registry=registry)
```

## What Happens During Registration

1. `registry.register(server)` stores the server in `_servers[server.name]`
2. Creates an `InProcessTransport` wrapping the server
3. Logs: `[ServerRegistry] Registered server='knowledge' tools=[...]`
4. Tools are immediately discoverable via `registry.list_tools()`

## Server Naming Rules

- Server names must be unique within the registry
- Names are lowercase, no spaces: `"knowledge"`, `"github"`, `"prometheus"`
- Registering a name twice replaces the previous server (with a warning)

## Tool Namespacing

When two servers expose a tool with the same name (e.g., both expose `search`):
```python
# No ambiguity — server is always explicit
registry.execute(server="knowledge", tool="search_documents", arguments={...})
registry.execute(server="github",    tool="search_code",      arguments={...})
```

## Viewing Registered Servers

```python
registry.list_servers()
# → ["knowledge"]

registry.list_tools()
# → [ToolDefinition(name="search_documents", server="knowledge"), ...]

registry.get_server("knowledge")
# → KnowledgeServer instance
```

## Future: Remote Transports

When external MCP servers are added (running as separate processes):

```python
# HTTP transport (MCP-over-HTTP)
from probe.mcp.transport.http import HttpTransport
registry.register(GitHubServer(), transport=HttpTransport("http://github-mcp:3000"))

# Stdio transport (MCP standard protocol)
from probe.mcp.transport.stdio import StdioTransport
registry.register(GitHubServer(), transport=StdioTransport("npx github-mcp-server"))
```

The `ServerRegistry` will be extended to accept an optional `transport` parameter.
`InProcessTransport` remains the default for local servers.
