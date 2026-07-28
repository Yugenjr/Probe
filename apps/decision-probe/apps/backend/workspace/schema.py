from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class BlockSchema(BaseModel):
    id: str
    type: str
    order: int
    content: dict

class ChatMessageSchema(BaseModel):
    id: str
    role: str
    content: str
    timestamp: datetime

class ExecutionLogSchema(BaseModel):
    id: str
    message: str
    success: bool
    timestamp: datetime

class WorkspaceMetadata(BaseModel):
    created_at: datetime
    updated_at: datetime
    version: int

class WorkspaceResponse(BaseModel):
    id: str
    title: str
    metadata: WorkspaceMetadata
    blocks: List[BlockSchema]
    conversations: List[ChatMessageSchema] = []
    execution_logs: List[ExecutionLogSchema] = []

class CreateWorkspaceRequest(BaseModel):
    title: str
    initial_blocks: Optional[List[dict]] = None

class UpdateWorkspaceRequest(BaseModel):
    title: Optional[str] = None
