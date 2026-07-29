# MCP Tool Lifecycle

## Tool Call Request Flow

```
1. Agent calls:
   result = await self.tool_gateway.execute(
       server="knowledge",
       tool="search_documents",
       arguments={"query": "ADWIN drift", "limit": 3}
   )

2. ToolGateway.execute()
   → logs debug entry
   → calls self._registry.execute(server, tool, arguments)

3. ServerRegistry.execute()
   → looks up transport for "knowledge"
   → calls InProcessTransport.call(tool_name, arguments)
   → times the call
   → catches all exceptions, wraps in ToolResult(success=False)

4. InProcessTransport.call()
   → calls KnowledgeServer.handle_tool_call("search_documents", args)

5. KnowledgeServer.handle_tool_call()
   → looks up SearchDocumentsTool in self._tools
   → calls self._executor.run(tool, arguments)

6. ToolExecutor.run()
   → times execution
   → calls SearchDocumentsTool.execute(**arguments)
   → catches TypeError (bad args) and Exception
   → injects execution_time_ms into result

7. SearchDocumentsTool.execute()
   → calls self._repo.search_documents(query, limit)
   → KnowledgeRepository.search_documents()
     → reads storage/knowledge/documents/*.json
     → keyword matches
     → returns list[dict]
   → wraps in ToolResult(success=True, content=..., artifacts=[...])

8. Result flows back up the stack unchanged
   → ToolResult arrives at the agent
```

## ToolResult Shape

```python
ToolResult(
    success=True,
    content="[psi-drift-diagnosis] Diagnosing PSI Drift...\n...",  # human-readable text
    artifacts=[{"id": "psi-drift-diagnosis", "title": "...", ...}],  # structured data
    metadata={"count": 3, "query": "ADWIN drift"},
    execution_time_ms=12,
    error=None
)
```

## ToolDefinition Shape

```python
ToolDefinition(
    name="search_documents",
    description="Search knowledge base articles using keyword matching.",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "limit": {"type": "integer", "default": 5}
        },
        "required": ["query"]
    },
    server="knowledge"
)
```

## Error Handling

Every layer handles errors and returns `ToolResult(success=False)`:

| Layer | Error handled |
|-------|--------------|
| `ToolExecutor` | `TypeError` (bad args), `Exception` |
| `ServerRegistry` | Missing server name, unhandled transport error |
| `ToolGateway` | Passed through from registry |

No exceptions propagate to the agent. The agent always receives a `ToolResult`.

## Tool Discovery

```python
# Agents can inspect available tools at any time
tools: list[ToolDefinition] = self.tool_gateway.discover_tools()

# Example output:
# [
#   ToolDefinition(name="search_documents", server="knowledge", ...),
#   ToolDefinition(name="get_document", server="knowledge", ...),
#   ToolDefinition(name="search_investigations", server="knowledge", ...),
#   ...
# ]
```

This enables future LLM-driven tool selection where the model decides which tools to call.
