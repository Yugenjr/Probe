"""Lightweight JSON-RPC Mock GitHub MCP Server running on port 8004."""
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="Mock GitHub MCP")

@app.post("/")
async def handle_rpc(request: Request):
    try:
        body = await request.json()
        method = body.get("method")
        rpc_id = body.get("id", 1)

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "result": {
                    "tools": [
                        {
                            "name": "search_code",
                            "description": "Search codebase repositories on GitHub.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string"},
                                    "limit": {"type": "integer", "default": 5}
                                },
                                "required": ["query"]
                            }
                        },
                        {
                            "name": "search_commits",
                            "description": "Search commit messages and changes on GitHub.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string"},
                                    "limit": {"type": "integer", "default": 5}
                                },
                                "required": ["query"]
                            }
                        }
                    ]
                },
                "id": rpc_id
            }
        elif method == "tools/call":
            params = body.get("params", {})
            tool_name = params.get("name", "unknown")
            return {
                "jsonrpc": "2.0",
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Mock GitHub response for '{tool_name}': Identified recent changes correlating with drift indicators."
                        }
                    ]
                },
                "id": rpc_id
            }
        else:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": "Method not found"},
                "id": rpc_id
            }
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"jsonrpc": "2.0", "error": {"code": -32700, "message": f"Parse error: {e}"}, "id": 1}
        )

if __name__ == "__main__":
    print("Starting Mock GitHub MCP server on port 8004...")
    uvicorn.run(app, host="127.0.0.1", port=8004)
