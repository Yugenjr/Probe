import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Well-known dependency patterns for common service types
SERVICE_DEPS = {
    "payments": ["PostgreSQL", "Redis", "Kafka", "Authentication Service"],
    "auth": ["PostgreSQL", "Redis", "Token Service"],
    "api-gateway": ["Authentication Service", "Rate Limiter", "payments"],
    "notification": ["Kafka", "SMTP Gateway", "Redis"],
    "billing": ["PostgreSQL", "payments", "Stripe Gateway"],
}

# Node type heuristics
TYPE_MAP = {
    "postgresql": "database", "postgres": "database", "mysql": "database",
    "redis": "cache", "memcached": "cache",
    "kafka": "queue", "rabbitmq": "queue", "sqs": "queue",
    "smtp": "external", "stripe": "external", "twilio": "external",
    "authentication": "service", "auth": "service", "token": "service",
    "rate": "service", "gateway": "service",
}


def _infer_node_type(name: str) -> str:
    name_lower = name.lower()
    for keyword, node_type in TYPE_MAP.items():
        if keyword in name_lower:
            return node_type
    return "service"


class ServiceDependencyAgent:
    """
    Stage 9 - Service Dependency Agent.

    Builds a dependency graph (nodes + edges) from evidence graph nodes,
    deployment data, and known service patterns.
    Edges represent real service-to-service or service-to-infrastructure relationships.
    """

    async def build_dependency_graph(
        self,
        graph: Dict[str, Any],
        deployments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Construct nodes and edges for the service dependency graph.
        """
        logger.info("ServiceDependencyAgent: building dependency graph.")

        nodes_in = graph.get("nodes", [])
        edges_in = graph.get("edges", [])

        node_registry: Dict[str, Dict] = {}
        edges_out = []

        # Seed nodes from existing evidence graph
        for n in nodes_in:
            nid = n.get("id", str(uuid.uuid4()))
            name = n.get("name", "unknown")
            node_registry[name.lower()] = {
                "id": nid,
                "name": name,
                "type": _infer_node_type(name),
            }

        # Enrich from deployment data — add touched services as nodes
        for dep in deployments.get("deployments", []):
            svc = dep.get("service", dep.get("description", ""))
            if svc and svc.lower() not in node_registry:
                node_registry[svc.lower()] = {
                    "id": str(uuid.uuid4()),
                    "name": svc,
                    "type": _infer_node_type(svc),
                }

        # If no nodes exist yet, seed common services
        if not node_registry:
            defaults = [
                ("payments-api", "service"),
                ("PostgreSQL", "database"),
                ("Redis", "cache"),
                ("Kafka", "queue"),
                ("Authentication Service", "service"),
            ]
            for name, ntype in defaults:
                node_registry[name.lower()] = {
                    "id": str(uuid.uuid4()),
                    "name": name,
                    "type": ntype,
                }

        # Build edges using existing evidence graph edges
        seen_edges = set()
        for e in edges_in:
            src_name = e.get("source", "")
            tgt_name = e.get("target", "")
            rel = e.get("type", "depends_on")
            key = (src_name.lower(), tgt_name.lower(), rel)
            if key not in seen_edges:
                seen_edges.add(key)
                edges_out.append({"source": src_name, "target": tgt_name, "relationship": rel})

        # Synthesize edges from known service dependency patterns
        for svc_key, deps in SERVICE_DEPS.items():
            matching_src = next(
                (n["name"] for k, n in node_registry.items() if svc_key in k), None
            )
            if not matching_src:
                continue
            for dep_name in deps:
                dep_lower = dep_name.lower()
                # Ensure dep node exists
                if dep_lower not in node_registry:
                    node_registry[dep_lower] = {
                        "id": str(uuid.uuid4()),
                        "name": dep_name,
                        "type": _infer_node_type(dep_name),
                    }
                key = (matching_src.lower(), dep_lower, "depends_on")
                if key not in seen_edges:
                    seen_edges.add(key)
                    edges_out.append({
                        "source": matching_src,
                        "target": dep_name,
                        "relationship": "depends_on",
                    })

        nodes_out = list(node_registry.values())
        logger.info(
            f"ServiceDependencyAgent: built graph with {len(nodes_out)} nodes and {len(edges_out)} edges."
        )

        return {
            "nodes": nodes_out,
            "edges": edges_out,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
