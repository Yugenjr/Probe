# MCP Architecture — DriftGuard Probe

## Overview

The Model Context Protocol (MCP) layer provides a **generic, extensible tool infrastructure** for all Probe agents. It enables agents to query external and internal knowledge sources without any coupling to specific servers, transports, or storage backends.

## Design Principles

1. **Agents never touch servers** — The Investigator knows about `ToolGateway`, not `KnowledgeServer`.
2. **Namespaced routing** — Every tool call is `execute(server="knowledge", tool="search_documents", ...)`. Ambiguity is impossible.
3. **No singletons** — `ServerRegistry` and `ToolGateway` are constructed once at startup and passed through DI.
4. **Typed contracts** — Every tool call returns `ToolResult`. Every tool exposes `ToolDefinition`. No loose dicts.
5. **Repository pattern** — Servers know about tools. Repositories know about storage. Clean separation.

## Layer Diagram

```
┌─────────────────────────────────────────────────┐
│                   Agents                        │
│        Investigator / Planner / Reporter        │
└──────────────────────┬──────────────────────────┘
                       │ tool_gateway.execute(...)
                       ▼
┌─────────────────────────────────────────────────┐
│               ToolGateway                        │
│      Single interface for all MCP tools          │
└──────────────────────┬──────────────────────────┘
                       │ registry.execute(server, tool, args)
                       ▼
┌─────────────────────────────────────────────────┐
│              ServerRegistry                      │
│   Maintains server map, routes to transports     │
└────────┬──────────────────────────┬─────────────┘
         │                          │
         ▼                          ▼
┌─────────────────┐      ┌─────────────────────┐
│ InProcessTransp │      │  HttpTransport        │
│ (local servers) │      │  (future: GitHub etc) │
└────────┬────────┘      └──────────┬────────────┘
         │                          │
         ▼                          ▼
┌─────────────────┐      ┌─────────────────────┐
│ KnowledgeServer │      │ GitHubServer (future) │
│ (BaseMCPServer) │      │ (BaseMCPServer)       │
└────────┬────────┘      └─────────────────────┘
         │
         ▼
┌─────────────────┐
│KnowledgeReposit.│  ← All I/O lives here
│  (filesystem)   │
│  (later: Qdrant)│
└─────────────────┘
```

## Module Layout

```
probe/mcp/
├── types.py             ToolResult, ToolDefinition, ToolRequest
├── server.py            BaseMCPServer abstract class
├── client/              MCPClientProtocol, InProcessMCPClient
├── registry/            ServerRegistry
├── transport/           InProcessTransport (+ future Http/Stdio)
├── gateway/             ToolGateway (what agents import)
├── tools/               BaseMCPTool, ToolExecutor
└── servers/
    └── knowledge/       KnowledgeServer, KnowledgeRepository, tools.py
```

## DI Wiring

At application startup (`probe/api/main.py`):
```python
mcp_registry = ServerRegistry()
mcp_registry.register(KnowledgeServer())

container.mcp_registry = mcp_registry
container.tool_gateway = ToolGateway(registry=mcp_registry)
```

The `AgentExecutor` passes `container.tool_gateway` to each agent constructor automatically.

## Adding a Future Server

```python
# 1. Implement BaseMCPServer
class GitHubServer(BaseMCPServer):
    @property
    def name(self): return "github"
    def get_tools(self): return [...]
    async def handle_tool_call(self, tool_name, arguments): ...

# 2. Register at startup (main.py only)
mcp_registry.register(GitHubServer(transport=HttpTransport("http://github-mcp:3000")))

# 3. Done. No agent changes required.
```
