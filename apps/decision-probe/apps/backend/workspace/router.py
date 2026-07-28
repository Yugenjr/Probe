from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel
from sqlmodel import Session, select
from typing import List
import os
import uuid

from storage.database import get_session
from storage.models import Workspace, Block, ChatMessage, ExecutionLog, Document, DocumentChunk
from services.document_processor import process_document_task
from retrieval.document import DocumentRetrievalAdapter
from services.planner import Planner
from services.investigator import Investigator
from services.timeline_builder import TimelineBuilder
from services.graph_builder import EvidenceGraphBuilder
from services.hypothesis_agent import HypothesisAgent
from services.critic_agent import CriticAgent
from services.decision_agent import DecisionAgent
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

class InvestigateRequest(BaseModel):
    goal: str

@router.post("/{id}/upload")
async def upload_document(
    id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
        
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower().strip(".")
    if ext not in ("pdf", "txt", "md", "log"):
        raise HTTPException(status_code=400, detail=f"Unsupported file format: .{ext}")
        
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    file_id = str(uuid.uuid4())
    stored_filename = f"{file_id}_{filename}"
    file_path = os.path.join(upload_dir, stored_filename)
    
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
        
    doc = Document(
        id=file_id,
        workspace_id=id,
        filename=filename,
        file_type=ext,
        file_path=file_path,
        status="pending"
    )
    session.add(doc)
    session.commit()
    session.refresh(doc)
    
    background_tasks.add_task(process_document_task, id, doc.id)
    
    return {
        "id": doc.id,
        "filename": doc.filename,
        "status": doc.status,
        "message": "File upload successful. Processing started in background."
    }

@router.post("/{id}/investigate")
async def investigate_workspace(
    id: str,
    request: InvestigateRequest,
    session: Session = Depends(get_session)
):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
        
    retrieval_adapter = DocumentRetrievalAdapter(session)
    chunks = await retrieval_adapter.retrieve(request.goal, context={"workspace_id": id, "limit": 5})
    
    planner = Planner()
    plan_dict = await planner.plan(request.goal, ws.title, chunks)
    
    investigator = Investigator()
    ws_metadata = {
        "title": ws.title,
        "created_at": ws.created_at.isoformat(),
        "version": ws.version
    }
    investigator_output = await investigator.investigate(plan_dict, chunks, ws_metadata)
    events = investigator_output.get("events", [])
    
    timeline_dict = TimelineBuilder.build_timeline(events)
    graph_dict = EvidenceGraphBuilder.build_graph(timeline_dict)
    
    entities = []
    seen_names = set()
    for node in graph_dict.get("nodes", []):
        name = node["name"]
        node_type = node["type"]
        if name.lower() not in seen_names:
            seen_names.add(name.lower())
            
            matching_chunk = "unknown"
            for ev in timeline_dict.get("events", []):
                if ev.get("service") == name.lower() or name.lower() in ev.get("description", "").lower():
                    matching_chunk = ev.get("source_chunk", "unknown")
                    break
            
            entities.append({
                "name": name,
                "type": node_type,
                "confidence": 0.95,
                "source_chunk": matching_chunk
            })
    evidence_dict = {"entities": entities}

    def save_or_update_block(block_type: str, content: dict):
        statement = select(Block).where(Block.workspace_id == id).where(Block.type == block_type)
        existing_block = session.exec(statement).first()
        if existing_block:
            existing_block.content = content
            session.add(existing_block)
            session.commit()
            session.refresh(existing_block)
        else:
            blocks_count = session.exec(select(Block).where(Block.workspace_id == id)).all()
            order = len(blocks_count)
            new_block = Block(
                workspace_id=id,
                type=block_type,
                order=order,
                content=content
            )
            session.add(new_block)
            session.commit()
            session.refresh(new_block)

    save_or_update_block("plan", plan_dict)
    save_or_update_block("timeline", timeline_dict)
    save_or_update_block("evidence", evidence_dict)
    save_or_update_block("graph", graph_dict)
    
    # Stage 3 reasoning agents
    hypotheses_agent = HypothesisAgent()
    hypotheses_dict = await hypotheses_agent.generate_hypotheses(
        plan_dict, timeline_dict, evidence_dict, graph_dict, chunks
    )
    
    critic_agent = CriticAgent()
    review_dict = await critic_agent.review_hypotheses(
        hypotheses_dict.get("hypotheses", []), timeline_dict, chunks
    )
    
    decision_agent = DecisionAgent()
    root_cause_dict = await decision_agent.decide_root_cause(
        hypotheses_dict.get("hypotheses", []), review_dict.get("reviews", []), chunks
    )
    
    save_or_update_block("hypotheses", hypotheses_dict)
    save_or_update_block("review", review_dict)
    save_or_update_block("root_cause", root_cause_dict)
        
    return {
        "plan": plan_dict,
        "timeline": timeline_dict,
        "evidence": evidence_dict,
        "graph": graph_dict,
        "hypotheses": hypotheses_dict,
        "review": review_dict,
        "root_cause": root_cause_dict
    }



@router.get("/{id}/plan")
def get_workspace_plan(id: str, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
        
    statement = select(Block).where(Block.workspace_id == id).where(Block.type == "plan")
    plan_block = session.exec(statement).first()
    if not plan_block:
        raise HTTPException(status_code=404, detail="No investigation plan found for this workspace")
        
    return plan_block.content

@router.get("/{id}/status")
def get_workspace_document_status(id: str, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
        
    statement = select(Document).where(Document.workspace_id == id)
    documents = session.exec(statement).all()
    
    doc_list = []
    all_indexed = True
    for doc in documents:
        doc_list.append({
            "id": doc.id,
            "filename": doc.filename,
            "file_type": doc.file_type,
            "status": doc.status,
            "chunk_count": doc.chunk_count,
            "error_message": doc.error_message,
            "created_at": doc.created_at.isoformat()
        })
        if doc.status in ("pending", "processing"):
            all_indexed = False
            
    return {
        "documents": doc_list,
        "all_indexed": all_indexed and len(documents) > 0,
        "document_count": len(documents)
    }

@router.get("/{id}/timeline")
def get_workspace_timeline(id: str, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    statement = select(Block).where(Block.workspace_id == id).where(Block.type == "timeline")
    block = session.exec(statement).first()
    if not block:
        raise HTTPException(status_code=404, detail="No timeline found for this workspace")
    return block.content

@router.get("/{id}/evidence")
def get_workspace_evidence(id: str, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    statement = select(Block).where(Block.workspace_id == id).where(Block.type == "evidence")
    block = session.exec(statement).first()
    if not block:
        raise HTTPException(status_code=404, detail="No evidence found for this workspace")
    return block.content

@router.get("/{id}/graph")
def get_workspace_graph(id: str, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    statement = select(Block).where(Block.workspace_id == id).where(Block.type == "graph")
    block = session.exec(statement).first()
    if not block:
        raise HTTPException(status_code=404, detail="No graph found for this workspace")
    return block.content

@router.get("/{id}/hypotheses")
def get_workspace_hypotheses(id: str, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    statement = select(Block).where(Block.workspace_id == id).where(Block.type == "hypotheses")
    block = session.exec(statement).first()
    if not block:
        raise HTTPException(status_code=404, detail="No hypotheses found for this workspace")
    return block.content

@router.get("/{id}/review")
def get_workspace_review(id: str, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    statement = select(Block).where(Block.workspace_id == id).where(Block.type == "review")
    block = session.exec(statement).first()
    if not block:
        raise HTTPException(status_code=404, detail="No review found for this workspace")
    return block.content

@router.get("/{id}/root-cause")
def get_workspace_root_cause(id: str, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    statement = select(Block).where(Block.workspace_id == id).where(Block.type == "root_cause")
    block = session.exec(statement).first()
    if not block:
        raise HTTPException(status_code=404, detail="No root cause decision found for this workspace")
    return block.content



