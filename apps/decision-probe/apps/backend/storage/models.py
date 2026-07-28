from typing import Optional, List
from datetime import datetime, timezone
import uuid
from sqlmodel import SQLModel, Field, Column, JSON

def utcnow():
    return datetime.now(timezone.utc)

class Workspace(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str
    version: int = Field(default=1)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    
class Block(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    workspace_id: str = Field(foreign_key="workspace.id", index=True)
    type: str
    order: int
    content: dict = Field(default_factory=dict, sa_column=Column(JSON))

class ChatMessage(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    workspace_id: str = Field(foreign_key="workspace.id", index=True)
    role: str
    content: str
    timestamp: datetime = Field(default_factory=utcnow)

class ExecutionLog(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    workspace_id: str = Field(foreign_key="workspace.id", index=True)
    message: str
    success: bool = Field(default=True)
    timestamp: datetime = Field(default_factory=utcnow)

class ProviderSetting(SQLModel, table=True):
    id: str = Field(primary_key=True) # e.g. 'gemini', 'groq'
    name: str
    enabled: bool = Field(default=True)
    status: str = Field(default="healthy")

class Document(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    workspace_id: str = Field(foreign_key="workspace.id", index=True)
    filename: str
    file_type: str  # pdf, txt, md, log
    file_path: str
    status: str = Field(default="pending")  # pending, processing, indexed, failed
    chunk_count: int = Field(default=0)
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

class DocumentChunk(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    document_id: str = Field(foreign_key="document.id", index=True)
    workspace_id: str = Field(foreign_key="workspace.id", index=True)
    chunk_index: int
    content: str
    embedding_json: str = Field(default="[]")  # Serialized JSON list of floats for cosine similarity search

