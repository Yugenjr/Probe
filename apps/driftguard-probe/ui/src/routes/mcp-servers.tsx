import { createFileRoute } from "@tanstack/react-router";
import { Cpu, Server, Activity, ArrowRight, Play, CheckCircle, XCircle, AlertCircle, RefreshCw } from "lucide-react";
import { useState, useEffect } from "react";
import { fetchMCPServers, fetchMCPTools, MCPServer, MCPTool } from "../lib/api-client";

export const Route = createFileRoute("/mcp-servers")({
  head: () => ({
    meta: [
      { title: "MCP Servers · DriftGuard Probe" },
      {
        name: "description",
        content: "Manage and monitor Model Context Protocol (MCP) integrations.",
      },
    ],
  }),
  component: MCPServersPage,
});

function MCPServersPage() {
  // Initialize state from localStorage cache if available
  const [servers, setServers] = useState<MCPServer[]>(() => {
    const cached = localStorage.getItem("mcp_servers_cache");
    return cached ? JSON.parse(cached) : [];
  });
  const [tools, setTools] = useState<MCPTool[]>(() => {
    const cached = localStorage.getItem("mcp_tools_cache");
    return cached ? JSON.parse(cached) : [];
  });
  const [activity, setActivity] = useState<any[]>([]);
  const [selectedServer, setSelectedServer] = useState<string | null>(() => {
    return localStorage.getItem("mcp_selected_server_cache") || null;
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = () => {
    setLoading(true);
    setError(null);
    Promise.all([fetchMCPServers(), fetchMCPTools()])
      .then(([serversData, toolsData]) => {
        setServers(serversData);
        setTools(toolsData);
        localStorage.setItem("mcp_servers_cache", JSON.stringify(serversData));
        localStorage.setItem("mcp_tools_cache", JSON.stringify(toolsData));
        
        if (serversData.length > 0 && !selectedServer) {
          setSelectedServer(serversData[0].name);
          localStorage.setItem("mcp_selected_server_cache", serversData[0].name);
        } else if (serversData.length > 0 && selectedServer) {
           // update selected server cache
           localStorage.setItem("mcp_selected_server_cache", selectedServer);
        }
        
        // Fetch activity
        return fetch("http://localhost:8006/api/v1/mcp/activity").then((res) => res.json());
      })
      .then((activityRes) => {
        if (activityRes && activityRes.data) {
          setActivity(activityRes.data.activity || []);
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load MCP servers page:", err);
        setError("Probe backend offline or MCP service unavailable. Showing cached data.");
        setLoading(false);
      });
  };

  // Update selected server cache when it changes
  useEffect(() => {
    if (selectedServer) {
      localStorage.setItem("mcp_selected_server_cache", selectedServer);
    }
  }, [selectedServer]);

  useEffect(() => {
    loadData();
  }, []);

  const activeServerObj = servers.find((s) => s.name === selectedServer);
  const serverTools = tools.filter((t) => t.server === selectedServer);

  return (
    <div className="mx-auto max-w-[1200px] px-4 py-6 md:px-8 md:py-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-[22px] font-semibold tracking-tight text-foreground flex items-center gap-2">
            <Cpu className="size-5 text-primary" />
            MCP Integrations
          </h1>
          <p className="mt-1 text-[13px] text-muted-foreground">
            Manage local and remote Model Context Protocol servers supplying real-time investigation evidence.
          </p>
        </div>
        <button
          onClick={loadData}
          className="inline-flex items-center gap-1.5 rounded-md border border-border bg-surface px-3 py-1.5 text-xs text-foreground hover:bg-accent transition"
        >
          <RefreshCw className="size-3.5" />
          Refresh
        </button>
      </div>

      {error && (
        <div className="rounded-lg border border-red-500/20 bg-red-500/5 px-4 py-4 text-center text-[13px] text-red-400">
          {error}
        </div>
      )}

      {/* Grid: Server Cards and Details panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Servers list */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-sm font-semibold text-foreground tracking-tight">Registered Servers</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {servers.map((server) => (
              <div
                key={server.name}
                onClick={() => setSelectedServer(server.name)}
                className={`p-4 rounded-xl border transition cursor-pointer flex flex-col justify-between h-36 ${
                  selectedServer === server.name
                    ? "border-primary/60 bg-primary/5 ring-1 ring-primary/30"
                    : "border-border bg-surface/50 hover:bg-surface"
                }`}
              >
                <div>
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-[14px] capitalize text-foreground flex items-center gap-1.5">
                      <Server className="size-4 text-muted-foreground" />
                      {server.name}
                    </span>
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium tracking-wide ${
                        server.status === "active"
                          ? "bg-emerald-500/10 text-emerald-400"
                          : "bg-rose-500/10 text-rose-400"
                      }`}
                    >
                      {server.status === "active" ? (
                        <>
                          <CheckCircle className="size-2.5" /> Connected
                        </>
                      ) : (
                        <>
                          <XCircle className="size-2.5" /> Offline
                        </>
                      )}
                    </span>
                  </div>
                  <div className="mt-2 text-xs text-muted-foreground flex gap-3">
                    <span>Type: <strong className="uppercase text-foreground">{server.type}</strong></span>
                    <span>Transport: <strong className="text-foreground">{server.transport}</strong></span>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-border/40 flex justify-between items-center text-xs text-muted-foreground">
                  <span>Latency: <strong className="text-foreground">{server.responseLatency}ms</strong></span>
                  <span>Tools: <strong className="text-foreground">{server.numberOfTools}</strong></span>
                </div>
              </div>
            ))}
          </div>

          {/* Grouped Tools Page */}
          <div className="pt-4 space-y-4">
            <h2 className="text-sm font-semibold text-foreground tracking-tight">All Discovered Tools</h2>
            <div className="border border-border rounded-xl bg-surface/30 divide-y divide-border overflow-hidden">
              {tools.map((tool) => (
                <div key={`${tool.server}-${tool.name}`} className="p-4 flex flex-col md:flex-row md:items-start justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-semibold text-primary">{tool.name}</span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted text-muted-foreground font-semibold uppercase">{tool.server}</span>
                    </div>
                    <p className="text-xs text-muted-foreground">{tool.description || "No tool description available."}</p>
                  </div>
                  <div className="text-[11px] text-muted-foreground font-mono self-end md:self-start">
                    Transport: {tool.transport}
                  </div>
                </div>
              ))}
              {tools.length === 0 && (
                <div className="p-8 text-center text-xs text-muted-foreground">No tools currently discovered.</div>
              )}
            </div>
          </div>
        </div>

        {/* Selected server details sidebar */}
        <div className="space-y-4">
          <h2 className="text-sm font-semibold text-foreground tracking-tight">Server Capabilities</h2>
          {activeServerObj ? (
            <div className="p-6 rounded-xl border border-border bg-surface/50 space-y-6">
              <div className="space-y-2">
                <h3 className="text-base font-semibold capitalize text-foreground">{activeServerObj.name} Details</h3>
                <div className="space-y-1 text-xs text-muted-foreground">
                  <div className="flex justify-between py-1 border-b border-border/30">
                    <span>Connection Status</span>
                    <span className={activeServerObj.connected ? "text-emerald-400 font-semibold" : "text-rose-400 font-semibold"}>
                      {activeServerObj.connected ? "Active" : "Offline"}
                    </span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-border/30">
                    <span>Transport Type</span>
                    <span className="text-foreground">{activeServerObj.transport}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-border/30">
                    <span>Latency</span>
                    <span className="text-foreground">{activeServerObj.responseLatency}ms</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-border/30">
                    <span>Health Check</span>
                    <span className="text-foreground">{activeServerObj.lastHealthCheck}</span>
                  </div>
                </div>
              </div>

              {/* Tools parameters panel */}
              <div className="space-y-4">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Available Tools & Parameters</h4>
                <div className="space-y-3">
                  {serverTools.map((tool) => (
                    <div key={tool.name} className="p-3 rounded-lg border border-border bg-surface/80 space-y-2">
                      <div className="font-mono text-xs font-semibold text-foreground">{tool.name}</div>
                      <div className="text-[11px] text-muted-foreground">{tool.description}</div>
                      
                      {tool.parameters && tool.parameters.properties && (
                        <div className="mt-2 space-y-1">
                          <span className="text-[10px] font-semibold text-muted-foreground uppercase">Parameters:</span>
                          <div className="grid grid-cols-2 gap-1 text-[10px] font-mono bg-muted/40 p-2 rounded">
                            {Object.entries(tool.parameters.properties).map(([key, prop]: [string, any]) => (
                              <div key={key} className="col-span-2 flex justify-between">
                                <span className="text-foreground">{key}</span>
                                <span className="text-muted-foreground">{prop.type || "string"}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                  {serverTools.length === 0 && (
                    <div className="text-xs text-muted-foreground">No registered tools found.</div>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="p-6 rounded-xl border border-dashed border-border bg-surface/30 text-center text-xs text-muted-foreground">
              Select an MCP server card to view capabilities.
            </div>
          )}
        </div>
      </div>

      {/* MCP Activity Section */}
      <div className="space-y-4">
        <h2 className="text-sm font-semibold text-foreground tracking-tight flex items-center gap-1.5">
          <Activity className="size-4 text-primary" />
          MCP Execution Activity Log
        </h2>
        <div className="border border-border rounded-xl bg-surface/30 overflow-hidden text-xs">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-muted/30 text-muted-foreground font-medium border-b border-border">
                <th className="p-3">Time</th>
                <th className="p-3">Server</th>
                <th className="p-3">Tool</th>
                <th className="p-3">Duration</th>
                <th className="p-3">Result</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {activity.map((act, index) => (
                <tr key={index} className="hover:bg-surface/10">
                  <td className="p-3 text-muted-foreground">
                    {new Date(act.timestamp * 1000).toLocaleTimeString()}
                  </td>
                  <td className="p-3 font-semibold text-foreground capitalize">{act.server}</td>
                  <td className="p-3 font-mono text-primary">{act.tool}</td>
                  <td className="p-3 text-foreground">{act.duration_ms}ms</td>
                  <td className="p-3">
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold ${
                        act.success
                          ? "bg-emerald-500/10 text-emerald-400"
                          : "bg-rose-500/10 text-rose-400"
                      }`}
                    >
                      {act.success ? "Success" : "Failed"}
                    </span>
                  </td>
                </tr>
              ))}
              {activity.length === 0 && (
                <tr>
                  <td colSpan={5} className="p-8 text-center text-muted-foreground">
                    No MCP tool calls logged in the current session.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
