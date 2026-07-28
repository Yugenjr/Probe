import pytest
import os
from services.timeline_builder import TimelineBuilder
from services.graph_builder import EvidenceGraphBuilder
from services.investigator import Investigator

def test_timeline_builder_normalization():
    # Test normalization of space to T, adding Z, and removing millisecond components
    ts1 = TimelineBuilder.normalize_timestamp("2026-07-24 10:41:12")
    assert ts1 == "2026-07-24T10:41:12Z"

    ts2 = TimelineBuilder.normalize_timestamp("2026-07-24T10:41:12.999Z")
    assert ts2 == "2026-07-24T10:41:12Z"

    ts3 = TimelineBuilder.normalize_timestamp("2026-07-24T10:41:12+00:00")
    assert ts3 == "2026-07-24T10:41:12Z"

def test_timeline_builder_merging_and_sorting():
    events = [
        {
            "timestamp": "2026-07-24 10:45:00",
            "type": "error",
            "service": "billing",
            "description": "Database connection timeout",
            "source_chunk": "chunk_2"
        },
        {
            "timestamp": "2026-07-24 10:40:00",
            "type": "deployment",
            "service": "payments",
            "description": "Released v1.2.0",
            "source_chunk": "chunk_1"
        },
        # Duplicate of first event but from a different source chunk
        {
            "timestamp": "2026-07-24 10:45:00",
            "type": "error",
            "service": "billing",
            "description": "Database connection timeout",
            "source_chunk": "chunk_3"
        }
    ]

    result = TimelineBuilder.build_timeline(events)
    timeline_events = result.get("events", [])

    # Verify duplicate was merged and chronological sorting (payments deployment is first)
    assert len(timeline_events) == 2
    
    # Check payments event
    assert timeline_events[0]["service"] == "payments"
    assert timeline_events[0]["timestamp"] == "2026-07-24T10:40:00Z"
    
    # Check billing event merged chunks: chunk_2 and chunk_3 sorted
    assert timeline_events[1]["service"] == "billing"
    assert timeline_events[1]["timestamp"] == "2026-07-24T10:45:00Z"
    assert "chunk_2" in timeline_events[1]["source_chunk"]
    assert "chunk_3" in timeline_events[1]["source_chunk"]

def test_graph_builder_rules():
    timeline = {
        "events": [
            {
                "timestamp": "2026-07-24T10:40:00Z",
                "type": "deployment",
                "service": "payments",
                "description": "Deployment ofpayments service triggered by admin user",
                "source_chunk": "chunk_1"
            },
            {
                "timestamp": "2026-07-24T10:41:00Z",
                "type": "error",
                "service": "payments",
                "description": "PostgreSQL exceeded connection limit inside connection pool",
                "source_chunk": "chunk_2"
            }
        ]
    }

    graph = EvidenceGraphBuilder.build_graph(timeline)
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    # Check node types
    node_types = {n["type"] for n in nodes}
    assert "Service" in node_types
    assert "Database" in node_types
    assert "Deployment" in node_types
    assert "Incident" in node_types

    # Find postgres node
    pg_node = next(n for n in nodes if n["id"] == "postgres")
    assert pg_node["type"] == "Database"

    # Find edges
    # We expect communications edge between service and database
    has_db_edge = any(e["source"] == "payments" and e["target"] == "postgres" and e["type"] == "communicates_with" for e in edges)
    assert has_db_edge

    # Incident should have failed_after link to deployment
    has_failed_after = any(e["type"] == "failed_after" for e in edges)
    assert has_failed_after

def test_investigator_mock_heuristics():
    investigator = Investigator()
    chunks = [
        {
            "id": "chunk_log_1",
            "snippet": "2026-07-24 10:41:12 [payments] ERROR: PostgreSQL pool connection timeout.",
            "title": "syslogs.txt"
        }
    ]
    
    result = investigator._generate_mock_events(chunks)
    events = result.get("events", [])

    assert len(events) == 1
    assert events[0]["timestamp"] == "2026-07-24T10:41:12Z"
    assert events[0]["service"] == "payments"
    assert events[0]["type"] == "error"
    assert "PostgreSQL pool connection timeout" in events[0]["description"]
    assert events[0]["source_chunk"] == "chunk_log_1"
