from pydantic import BaseModel
from typing import List

class DependencyNode(BaseModel):
    id: str
    name: str
    type: str  # service | database | queue | cache | external

class DependencyEdge(BaseModel):
    source: str
    target: str
    relationship: str  # depends_on | calls | reads_from | writes_to

class DependencyGraphResponse(BaseModel):
    nodes: List[DependencyNode]
    edges: List[DependencyEdge]
    generated_at: str = ""
