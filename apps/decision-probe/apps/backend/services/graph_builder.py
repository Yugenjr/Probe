import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class EvidenceGraphBuilder:
    @staticmethod
    def build_graph(timeline: Dict[str, Any]) -> Dict[str, Any]:
        """
        Builds a backend graph structure of unique Nodes and Edges from chronological events.
        
        Node Types: Service, Component, Database, API, Deployment, Incident, User
        Edge Types: triggered, depends_on, communicates_with, failed_after, affected, references
        """
        events = timeline.get("events", [])
        nodes_map = {}
        edges_list = []

        def add_node(node_id: str, name: str, node_type: str):
            nid = node_id.lower().strip().replace(" ", "_")
            if not nid:
                return None
            if nid not in nodes_map:
                nodes_map[nid] = {
                    "id": nid,
                    "name": name,
                    "type": node_type
                }
            return nid

        def add_edge(source: str, target: str, edge_type: str):
            src = source.lower().strip().replace(" ", "_")
            tgt = target.lower().strip().replace(" ", "_")
            if not src or not tgt or src == tgt:
                return
            # Avoid duplicate edges
            for edge in edges_list:
                if edge["source"] == src and edge["target"] == tgt and edge["type"] == edge_type:
                    return
            edges_list.append({
                "source": src,
                "target": tgt,
                "type": edge_type
            })

        last_deployment_id = None

        for idx, event in enumerate(events):
            desc = event.get("description", "")
            desc_lower = desc.lower()
            service_name = event.get("service", "unknown")
            event_type = event.get("type", "info")
            chunk_ref = event.get("source_chunk", "unknown")

            # 1. Add Service Node (all events are associated with a service/system)
            service_id = add_node(service_name, service_name.capitalize(), "Service")

            # 2. Add Component Node if component keywords match
            component_id = None
            for comp_keyword in ("broker", "queue", "gateway", "cache", "dashboard", "frontend", "backend", "balancer"):
                if comp_keyword in desc_lower:
                    component_id = add_node(comp_keyword, comp_keyword.capitalize(), "Component")
                    if service_id:
                        add_edge(service_id, component_id, "depends_on")
                    break

            # 3. Add Database Node if database keywords match
            database_id = None
            for db_keyword in ("postgres", "postgresql", "mysql", "redis", "mongodb", "sqlite", "database", "db"):
                if db_keyword in desc_lower:
                    db_name = "PostgreSQL" if "postgres" in db_keyword else db_keyword.capitalize()
                    database_id = add_node(db_keyword, db_name, "Database")
                    if service_id:
                        add_edge(service_id, database_id, "communicates_with")
                    break

            # 4. Add API Node if api keywords match
            api_id = None
            if any(k in desc_lower for k in ("api", "endpoint", "http", "grpc", "url", "route")):
                api_id = add_node(f"{service_name}_api", f"{service_name.capitalize()} API", "API")
                if service_id:
                    add_edge(service_id, api_id, "communicates_with")

            # 5. Add User Node if user keyword matches
            user_id = None
            user_match = None
            if "user" in desc_lower or "maya" in desc_lower:
                user_name = "Maya" if "maya" in desc_lower else "System User"
                user_id = add_node(user_name.lower(), user_name, "User")
                if service_id:
                    add_edge(user_id, service_id, "communicates_with")

            # 6. Add Deployment Node
            if event_type == "deployment" or "deploy" in desc_lower or "release" in desc_lower:
                deploy_id = add_node(f"deploy_{idx}", f"Deployment {event['timestamp']}", "Deployment")
                last_deployment_id = deploy_id
                if service_id:
                    add_edge(service_id, deploy_id, "references")

            # 7. Add Incident Node (for errors or failures)
            if event_type == "error" or "error" in desc_lower or "fail" in desc_lower or "timeout" in desc_lower:
                incident_title = desc[:30] + ("..." if len(desc) > 30 else "")
                incident_id = add_node(f"incident_{idx}", incident_title, "Incident")
                
                if service_id:
                    add_edge(service_id, incident_id, "affected")
                if database_id:
                    add_edge(database_id, incident_id, "affected")
                if component_id:
                    add_edge(component_id, incident_id, "affected")
                
                # Check if this incident happened after a deployment
                if last_deployment_id:
                    add_edge(incident_id, last_deployment_id, "failed_after")
                
                # Check if a user triggered this incident
                if user_id and ("login" in desc_lower or "trigger" in desc_lower):
                    add_edge(user_id, incident_id, "triggered")

        return {
            "nodes": list(nodes_map.values()),
            "edges": edges_list
        }
