# Model Context Protocol (MCP) Integration

DriftGuard Probe is **MCP-Native**.  
Every investigation tool is designed to function as an independent tool invocation that can run either over an in-memory REST client or an out-of-process Model Context Protocol transport.

## Why MCP?
The Model Context Protocol establishes a standard communication layer between AI agents and external tools or data sources. By separating tool definitions from transport implementation:
- Agents require zero code changes when migrating from REST to MCP.
- External systems can connect directly to Probe's MCP server (`probe/mcp/server.py`) to leverage investigation tools directly from standard AI environments (Claude Desktop, specialized copilot IDEs, etc.).

## Supported Initial MCP Tool Contracts
- `get_model`: Fetch configuration and version lineage for a registered ML model.
- `get_metrics`: Retrieve real-time or historical telemetry metrics.
- `get_drift`: Extract drift indicators and feature-level statistical distributions.
- `get_validation`: Retrieve data validation check records.
- `get_audit`: Retrieve audit log trails and historical operational actions.
- `get_reports`: Extract previously compiled diagnostic reports.
- `search_history`: Search vector memory for analogous historical incidents.
- `run_experiment`: Trigger a sandbox analytical run or replay test.
