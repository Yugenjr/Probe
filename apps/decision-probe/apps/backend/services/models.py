from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class ResourceBundle(BaseModel):
    documents: List[Dict[str, Any]] = Field(default_factory=list)
    web_results: List[Dict[str, Any]] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)

class ExecutionPlan(BaseModel):
    retrieve_web: bool = False
    retrieve_documents: bool = False
    retrieve_workspace_history: bool = False
    needs_reasoning: bool = True
    generate_summary: bool = False

class ReasoningContext(BaseModel):
    workspace_id: str
    workspace_title: str
    user_prompt: str
    system_prompt: str = ""
    timestamp: datetime
    
    conversation: List[Dict[str, Any]] = Field(default_factory=list)
    blocks: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Settings and Config
    settings: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # New Requested Fields
    workspace_description: str = ""
    timeline: List[Dict[str, Any]] = Field(default_factory=list)
    current_decisions: List[Dict[str, Any]] = Field(default_factory=list)
    provider_configuration: Dict[str, Any] = Field(default_factory=dict)
    planner_output: Optional[ExecutionPlan] = None
    
    # Aggregated Resources from the Planner's execution
    resources: ResourceBundle = Field(default_factory=ResourceBundle)
