"""Unit tests for the Knowledge MCP Server and its tools."""
import json
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from probe.mcp.servers.knowledge.repository import KnowledgeRepository
from probe.mcp.servers.knowledge.server import KnowledgeServer
from probe.mcp.types import ToolResult


@pytest.fixture
def temp_knowledge_dir():
    """Create a temporary directory seeded with sample knowledge documents and runbooks."""
    with TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        docs_dir = base / "documents"
        runbooks_dir = base / "runbooks"
        docs_dir.mkdir(parents=True)
        runbooks_dir.mkdir(parents=True)

        # Seed JSON article
        doc1 = {
            "id": "test-doc-1",
            "title": "Diagnosing PSI Drift on User Data",
            "category": "Playbook",
            "tags": ["PSI", "drift"],
            "content": "Detailed content about user feature distribution shifts and thresholds."
        }
        (docs_dir / "test-doc-1.json").write_text(json.dumps(doc1), encoding="utf-8")

        # Seed markdown runbook
        runbook1 = (
            "# Retrain Decision Tree\n"
            "Steps to trigger retraining when drift occurs."
        )
        (runbooks_dir / "retrain-decision-tree.md").write_text(runbook1, encoding="utf-8")

        yield tmpdir


@pytest.mark.anyio
async def test_knowledge_server_tools(temp_knowledge_dir):
    """Test all KnowledgeServer tools using seeded temporary storage."""
    repo = KnowledgeRepository(base_dir=temp_knowledge_dir)
    server = KnowledgeServer(repository=repo)

    # 1. list_documents
    res = await server.handle_tool_call("list_documents", {"limit": 5})
    assert res.success is True
    assert res.metadata["count"] == 1
    assert "test-doc-1" in res.content

    # 2. search_documents
    res = await server.handle_tool_call("search_documents", {"query": "PSI drift", "limit": 2})
    assert res.success is True
    assert res.metadata["count"] == 1
    assert "test-doc-1" in res.content

    # 3. get_document
    res = await server.handle_tool_call("get_document", {"doc_id": "test-doc-1"})
    assert res.success is True
    assert "Detailed content" in res.content

    res_fail = await server.handle_tool_call("get_document", {"doc_id": "missing-doc"})
    assert res_fail.success is False

    # 4. search_runbooks
    res = await server.handle_tool_call("search_runbooks", {"query": "retraining"})
    assert res.success is True
    assert res.metadata["count"] == 1
    assert "Retrain Decision Tree" in res.content

    # 5. search_investigations (empty since no sessions in temp run)
    res = await server.handle_tool_call("search_investigations", {"model_id": "test-model"})
    assert res.success is True
    assert res.metadata["count"] == 0
