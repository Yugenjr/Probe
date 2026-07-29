"""MCP servers package.

Registered servers:
  knowledge  →  KnowledgeServer    (documents, runbooks, investigation history)

Future servers (register only — no agent changes needed):
  github     →  GitHubServer
  prometheus →  PrometheusServer
  grafana    →  GrafanaServer
  mlflow     →  MLflowServer
"""
from .knowledge.server import KnowledgeServer

__all__ = ["KnowledgeServer"]
