from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select
from typing import List

from storage.database import get_session
from storage.models import Workspace, Block, ChatMessage, ExecutionLog
from .schema import (
    WorkspaceResponse, CreateWorkspaceRequest, WorkspaceMetadata, 
    BlockSchema, UpdateWorkspaceRequest, ChatMessageSchema, ExecutionLogSchema
)

router = APIRouter(prefix="/api/v1/workspaces", tags=["Workspaces"])

@router.post("", response_model=WorkspaceResponse)
def create_workspace(request: CreateWorkspaceRequest, session: Session = Depends(get_session)):
    ws = Workspace(title=request.title)
    session.add(ws)
    session.commit()
    session.refresh(ws)
    
    blocks_out = []
    if request.initial_blocks:
        for idx, b in enumerate(request.initial_blocks):
            block = Block(
                workspace_id=ws.id,
                type=b.get("type", "text"),
                order=idx,
                content=b.get("content", {})
            )
            session.add(block)
            session.commit()
            session.refresh(block)
            blocks_out.append(BlockSchema(id=block.id, type=block.type, order=block.order, content=block.content))
            
    return WorkspaceResponse(
        id=ws.id,
        title=ws.title,
        metadata=WorkspaceMetadata(
            created_at=ws.created_at,
            updated_at=ws.updated_at,
            version=ws.version
        ),
        blocks=blocks_out
    )

@router.get("", response_model=List[WorkspaceResponse])
def list_workspaces(session: Session = Depends(get_session)):
    workspaces = session.exec(select(Workspace)).all()
    out = []
    for ws in workspaces:
        blocks = session.exec(select(Block).where(Block.workspace_id == ws.id).order_by(Block.order)).all()
        blocks_out = [BlockSchema(id=b.id, type=b.type, order=b.order, content=b.content) for b in blocks]
        
        chat = session.exec(select(ChatMessage).where(ChatMessage.workspace_id == ws.id).order_by(ChatMessage.timestamp)).all()
        chat_out = [ChatMessageSchema(id=c.id, role=c.role, content=c.content, timestamp=c.timestamp) for c in chat]
        
        logs = session.exec(select(ExecutionLog).where(ExecutionLog.workspace_id == ws.id).order_by(ExecutionLog.timestamp)).all()
        logs_out = [ExecutionLogSchema(id=l.id, message=l.message, success=l.success, timestamp=l.timestamp) for l in logs]
        
        out.append(WorkspaceResponse(
            id=ws.id,
            title=ws.title,
            metadata=WorkspaceMetadata(
                created_at=ws.created_at,
                updated_at=ws.updated_at,
                version=ws.version
            ),
            blocks=blocks_out,
            conversations=chat_out,
            execution_logs=logs_out
        ))
    return out

@router.get("/{id}", response_model=WorkspaceResponse)
def get_workspace(id: str, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
        
    blocks = session.exec(select(Block).where(Block.workspace_id == ws.id).order_by(Block.order)).all()
    blocks_out = [BlockSchema(id=b.id, type=b.type, order=b.order, content=b.content) for b in blocks]
    
    chat = session.exec(select(ChatMessage).where(ChatMessage.workspace_id == ws.id).order_by(ChatMessage.timestamp)).all()
    chat_out = [ChatMessageSchema(id=c.id, role=c.role, content=c.content, timestamp=c.timestamp) for c in chat]
    
    logs = session.exec(select(ExecutionLog).where(ExecutionLog.workspace_id == ws.id).order_by(ExecutionLog.timestamp)).all()
    logs_out = [ExecutionLogSchema(id=l.id, message=l.message, success=l.success, timestamp=l.timestamp) for l in logs]
    
    return WorkspaceResponse(
        id=ws.id,
        title=ws.title,
        metadata=WorkspaceMetadata(
            created_at=ws.created_at,
            updated_at=ws.updated_at,
            version=ws.version
        ),
        blocks=blocks_out,
        conversations=chat_out,
        execution_logs=logs_out
    )

@router.put("/{id}", response_model=WorkspaceResponse)
def update_workspace(id: str, request: UpdateWorkspaceRequest, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    if request.title is not None:
        ws.title = request.title
    
    session.add(ws)
    session.commit()
    session.refresh(ws)
    
    # Return updated workspace
    return get_workspace(id, session)

@router.delete("/{id}")
def delete_workspace(id: str, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    blocks = session.exec(select(Block).where(Block.workspace_id == ws.id)).all()
    for b in blocks:
        session.delete(b)
        
    session.delete(ws)
    session.commit()
    return {"status": "deleted"}

class ChatRequest(BaseModel):
    message: str

from fastapi.responses import StreamingResponse
import json
import asyncio

from services.reasoning_engine import ReasoningEngine
from inference.client import InferenceClient

@router.post("/{id}/chat")
async def chat_workspace(id: str, request: ChatRequest, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
        
    user_msg = ChatMessage(workspace_id=id, role="user", content=request.message)
    session.add(user_msg)
    session.commit()
    session.refresh(user_msg)
        
    client = InferenceClient()
    engine = ReasoningEngine(session, client)
    
    async def stream_with_user_msg():
        yield f"data: {json.dumps({'type': 'chat_message', 'payload': {'id': user_msg.id, 'role': user_msg.role, 'content': user_msg.content, 'timestamp': user_msg.timestamp.isoformat()}})}\n\n"
        async for chunk in engine.execute_and_stream(id, request.message):
            yield chunk
            
    return StreamingResponse(
        stream_with_user_msg(),
        media_type="text/event-stream"
    )

@router.get("/{id}/export")
def export_workspace(id: str, format: str = "json", session: Session = Depends(get_session)):
    ws_data = get_workspace(id, session)
    if format == "json":
        return ws_data
    return {"message": f"Export format {format} not fully implemented yet."}

from fastapi import UploadFile, File

@router.post("/{id}/resources")
async def upload_resource(id: str, file: UploadFile = File(...), session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
        
    # Calculate next order
    blocks_count = session.exec(select(Block).where(Block.workspace_id == id)).all()
    order = len(blocks_count)
    
    # Create Evidence Block for the uploaded file
    content = {
        "title": file.filename,
        "source": "Uploaded File",
        "type": "document" if file.filename.endswith(".pdf") else "csv" if file.filename.endswith(".csv") else "unknown"
    }
    
    block = Block(
        workspace_id=id,
        type="evidence",
        order=order,
        content=content
    )
    
    session.add(block)
    session.commit()
    session.refresh(block)
    
    return BlockSchema(id=block.id, type=block.type, order=block.order, content=block.content)

from pydantic import BaseModel
from storage.models import ProviderSetting

class ProviderUpdate(BaseModel):
    enabled: bool

@router.get("/settings/providers")
def get_providers(session: Session = Depends(get_session)):
    providers = session.exec(select(ProviderSetting)).all()
    if not providers:
        # Seed default providers if table is empty
        defaults = [
            ProviderSetting(id="gemini", name="Gemini (Google)", enabled=True, status="healthy"),
            ProviderSetting(id="groq", name="Groq", enabled=True, status="healthy"),
            ProviderSetting(id="openrouter", name="OpenRouter", enabled=False, status="unknown")
        ]
        for p in defaults:
            session.add(p)
        session.commit()
        providers = session.exec(select(ProviderSetting)).all()
    return providers

@router.put("/settings/providers/{provider_id}")
def update_provider(provider_id: str, update: ProviderUpdate, session: Session = Depends(get_session)):
    provider = session.get(ProviderSetting, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    provider.enabled = update.enabled
    session.add(provider)
    session.commit()
    session.refresh(provider)
    return provider
