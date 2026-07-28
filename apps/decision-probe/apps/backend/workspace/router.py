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
from services.validation_agent import ValidationAgent
from services.remediation_agent import RemediationAgent
from services.evidence_gap_agent import EvidenceGapAgent
from services.evidence_acquisition_agent import EvidenceAcquisitionAgent
from services.investigation_loop_agent import InvestigationLoopAgent
from services.external.log_collector_agent import LogCollectorAgent
from services.external.metrics_collector_agent import MetricsCollectorAgent
from services.external.deployment_collector_agent import DeploymentCollectorAgent
from services.external.git_change_agent import GitChangeAgent
from services.evidence_fusion_agent import EvidenceFusionAgent
from services.severity_agent import SeverityAgent
from services.incident_commander_agent import IncidentCommanderAgent
from services.response_planner_agent import ResponsePlannerAgent
from services.communication_agent import CommunicationAgent
from services.resolution_tracker_agent import ResolutionTrackerAgent
from services.knowledge_agent import KnowledgeAgent
from services.knowledge.embedding_agent import EmbeddingAgent
from services.knowledge.incident_retrieval_agent import IncidentRetrievalAgent
from services.knowledge.similarity_agent import SimilarityAgent
from services.knowledge.learning_agent import LearningAgent
from services.knowledge.pattern_detection_agent import PatternDetectionAgent
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
    
    # Stage 4 validation agent
    validation_agent = ValidationAgent()
    validation_dict = await validation_agent.validate_root_cause(
        root_cause_dict.get("root_cause", {}), timeline_dict, graph_dict, chunks
    )
    save_or_update_block("validation", validation_dict)
    
    # Stage 5 investigation loop
    # 1. Load previous iterations
    iter_statement = select(Block).where(Block.workspace_id == id).where(Block.type == "investigation_iteration")
    existing_iterations_block = session.exec(iter_statement).first()
    if existing_iterations_block and existing_iterations_block.content:
        previous_iterations = existing_iterations_block.content.get("iterations", [])
    else:
        previous_iterations = []

    # 2. Run Evidence Gap Agent
    evidence_gap_agent = EvidenceGapAgent()
    evidence_gap_dict = await evidence_gap_agent.analyze_gaps(
        root_cause_dict, validation_dict, review_dict.get("reviews", []), timeline_dict
    )
    save_or_update_block("evidence_gap", evidence_gap_dict)

    # 3. Run Evidence Acquisition Agent
    evidence_acquisition_agent = EvidenceAcquisitionAgent()
    evidence_request_dict = await evidence_acquisition_agent.generate_requests(evidence_gap_dict)
    save_or_update_block("evidence_request", evidence_request_dict)

    # 4. Run Investigation Loop Agent
    investigation_loop_agent = InvestigationLoopAgent()
    iteration_dict = await investigation_loop_agent.evaluate_iteration(
        previous_iterations,
        root_cause_dict.get("root_cause", {}).get("confidence", 0.0),
        evidence_gap_dict.get("should_continue", True)
    )
    all_iterations = previous_iterations + [iteration_dict]
    iterations_block_content = {"iterations": all_iterations}
    save_or_update_block("investigation_iteration", iterations_block_content)

    # 5. Run Remediation Agent
    remediation_agent = RemediationAgent()
    remediation_dict = await remediation_agent.generate_remediation(
        root_cause_dict.get("root_cause", {}), validation_dict, chunks
    )
    save_or_update_block("remediation", remediation_dict)
        
    return {
        "plan": plan_dict,
        "timeline": timeline_dict,
        "evidence": evidence_dict,
        "graph": graph_dict,
        "hypotheses": hypotheses_dict,
        "review": review_dict,
        "root_cause": root_cause_dict,
        "validation": validation_dict,
        "evidence_gap": evidence_gap_dict,
        "evidence_requests": evidence_request_dict,
        "investigation_iterations": iterations_block_content,
        "remediation": remediation_dict
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

@router.get("/{id}/validation")
def get_workspace_validation(id: str, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    statement = select(Block).where(Block.workspace_id == id).where(Block.type == "validation")
    block = session.exec(statement).first()
    if not block:
        raise HTTPException(status_code=404, detail="No validation found for this workspace")
    return block.content

@router.get("/{id}/remediation")
def get_workspace_remediation(id: str, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    statement = select(Block).where(Block.workspace_id == id).where(Block.type == "remediation")
    block = session.exec(statement).first()
    if not block:
        raise HTTPException(status_code=404, detail="No remediation found for this workspace")
    return block.content

@router.get("/{id}/evidence-gaps")
def get_workspace_evidence_gaps(id: str, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    statement = select(Block).where(Block.workspace_id == id).where(Block.type == "evidence_gap")
    block = session.exec(statement).first()
    if not block:
        raise HTTPException(status_code=404, detail="No evidence gap block found for this workspace")
    return block.content

@router.get("/{id}/evidence-requests")
def get_workspace_evidence_requests(id: str, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    statement = select(Block).where(Block.workspace_id == id).where(Block.type == "evidence_request")
    block = session.exec(statement).first()
    if not block:
        raise HTTPException(status_code=404, detail="No evidence request block found for this workspace")
    return block.content

@router.get("/{id}/iterations")
def get_workspace_iterations(id: str, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    statement = select(Block).where(Block.workspace_id == id).where(Block.type == "investigation_iteration")
    block = session.exec(statement).first()
    if not block:
        raise HTTPException(status_code=404, detail="No iteration block found for this workspace")
    return block.content

@router.post("/{id}/collect-evidence")
async def collect_workspace_evidence(id: str, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Initialize Stage 6 Collector Agents
    log_collector = LogCollectorAgent()
    metrics_collector = MetricsCollectorAgent()
    deploy_collector = DeploymentCollectorAgent()
    git_collector = GitChangeAgent()

    # Fetch and normalize feeds
    raw_logs = await log_collector.fetch("payments", "last_hour")
    logs_dict = log_collector.normalize(raw_logs)
    
    raw_metrics = await metrics_collector.fetch("payments", "last_hour")
    metrics_dict = metrics_collector.normalize(raw_metrics)
    
    raw_deploys = await deploy_collector.fetch("last_hour")
    deployments_dict = deploy_collector.normalize(raw_deploys)
    
    raw_commits = await git_collector.fetch()
    git_changes_dict = git_collector.normalize(raw_commits)

    # Fetch existing chunks to pass to Fusion Agent
    stmt = select(DocumentChunk).where(DocumentChunk.workspace_id == id)
    db_chunks = session.exec(stmt).all()
    existing_chunks = []
    for c in db_chunks:
        existing_chunks.append({
            "id": c.id,
            "document_id": c.document_id,
            "snippet": c.content
        })

    # Execute Evidence Fusion
    fusion_agent = EvidenceFusionAgent()
    fused_dict = await fusion_agent.fuse_evidence(
        existing_chunks, logs_dict, metrics_dict, deployments_dict, git_changes_dict
    )

    # Save blocks using helper
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

    save_or_update_block("external_evidence", logs_dict)
    save_or_update_block("deployment_changes", deployments_dict)
    save_or_update_block("metric_analysis", metrics_dict)
    save_or_update_block("git_analysis", git_changes_dict)

    # Upgrade the Evidence Graph block with fused updates
    graph_stmt = select(Block).where(Block.workspace_id == id).where(Block.type == "graph")
    existing_graph_block = session.exec(graph_stmt).first()
    if existing_graph_block and existing_graph_block.content:
        graph_content = existing_graph_block.content
        nodes_list = graph_content.get("nodes", [])
        edges_list = graph_content.get("edges", [])
        
        for update in fused_dict.get("graph_updates", []):
            for n in update.get("nodes", []):
                if not any(item.get("id") == n.get("id") for item in nodes_list):
                    nodes_list.append(n)
            for e in update.get("edges", []):
                if not any(item.get("source") == e.get("source") and item.get("target") == e.get("target") and item.get("type") == e.get("type") for item in edges_list):
                    edges_list.append(e)
                    
        existing_graph_block.content = {
            "nodes": list(nodes_list),
            "edges": list(edges_list)
        }
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(existing_graph_block, "content")
        session.add(existing_graph_block)
        session.commit()

    return {
        "logs": logs_dict,
        "metrics": metrics_dict,
        "deployments": deployments_dict,
        "git_changes": git_changes_dict,
        "fused_evidence": fused_dict
    }

@router.get("/{id}/external-evidence")
def get_workspace_external_evidence(id: str, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    statement = select(Block).where(Block.workspace_id == id).where(Block.type == "external_evidence")
    block = session.exec(statement).first()
    if not block:
        raise HTTPException(status_code=404, detail="No external evidence found for this workspace")
    return block.content

@router.get("/{id}/changes")
def get_workspace_changes(id: str, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    statement = select(Block).where(Block.workspace_id == id).where(Block.type == "deployment_changes")
    block = session.exec(statement).first()
    if not block:
        raise HTTPException(status_code=404, detail="No deployment changes found for this workspace")
    return block.content

@router.get("/{id}/metrics")
def get_workspace_metrics(id: str, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    statement = select(Block).where(Block.workspace_id == id).where(Block.type == "metric_analysis")
    block = session.exec(statement).first()
    if not block:
        raise HTTPException(status_code=404, detail="No metric analysis found for this workspace")
    return block.content

@router.post("/{id}/create-incident")
async def create_workspace_incident(id: str, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Load root cause block
    rc_stmt = select(Block).where(Block.workspace_id == id).where(Block.type == "root_cause")
    rc_block = session.exec(rc_stmt).first()
    rc_dict = rc_block.content if rc_block else {"root_cause": {"title": "Database connection pool exhaustion", "description": "Connection pool size limit was hit", "confidence": 0.75}}

    # Load remediation block
    rem_stmt = select(Block).where(Block.workspace_id == id).where(Block.type == "remediation")
    rem_block = session.exec(rem_stmt).first()
    rem_dict = rem_block.content if rem_block else {"immediate_actions": ["Increase database connections pool limit"], "permanent_fixes": ["Implement adaptive pooling"], "prevention_steps": ["Add database saturation alerts"]}

    # Load metrics block (if any)
    metrics_stmt = select(Block).where(Block.workspace_id == id).where(Block.type == "metric_analysis")
    metrics_block = session.exec(metrics_stmt).first()
    metrics_dict = metrics_block.content if metrics_block else {"metrics": [{"name": "db_connections", "value": 98.0}]}

    # Initialize Stage 7 Agents
    sev_agent = SeverityAgent()
    severity_dict = await sev_agent.classify_severity(rc_dict, metrics_dict)

    commander_agent = IncidentCommanderAgent()
    incident_dict = await commander_agent.generate_overview(rc_dict)

    planner_agent = ResponsePlannerAgent()
    response_plan_dict = await planner_agent.generate_response_plan(incident_dict, rem_dict)

    comm_agent = CommunicationAgent()
    comm_dict = await comm_agent.generate_updates(incident_dict, severity_dict)

    tracker_agent = ResolutionTrackerAgent()
    resolution_dict = await tracker_agent.evaluate_resolution(response_plan_dict.get("tasks", []), rem_dict)

    knowledge_agent = KnowledgeAgent()
    knowledge_dict = await knowledge_agent.generate_knowledge(rc_dict, rem_dict)

    # Helper function to save blocks
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

    # Persist all blocks in DB
    save_or_update_block("incident_summary", incident_dict)
    save_or_update_block("severity", severity_dict)
    save_or_update_block("response_plan", response_plan_dict)
    save_or_update_block("communication", comm_dict)
    save_or_update_block("resolution", resolution_dict)
    save_or_update_block("incident_knowledge", knowledge_dict)

    return {
        "incident": incident_dict,
        "severity": severity_dict,
        "response_plan": response_plan_dict,
        "communications": comm_dict,
        "resolution": resolution_dict
    }

@router.get("/{id}/incident")
def get_workspace_incident(id: str, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    statement = select(Block).where(Block.workspace_id == id).where(Block.type == "incident_summary")
    block = session.exec(statement).first()
    if not block:
        raise HTTPException(status_code=404, detail="No incident summary found for this workspace")
    return block.content

@router.get("/{id}/tasks")
def get_workspace_tasks(id: str, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    statement = select(Block).where(Block.workspace_id == id).where(Block.type == "response_plan")
    block = session.exec(statement).first()
    if not block:
        raise HTTPException(status_code=404, detail="No response tasks found for this workspace")
    return block.content

@router.get("/{id}/resolution")
def get_workspace_resolution(id: str, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    statement = select(Block).where(Block.workspace_id == id).where(Block.type == "resolution")
    block = session.exec(statement).first()
    if not block:
        raise HTTPException(status_code=404, detail="No resolution details found for this workspace")
    return block.content

@router.get("/{id}/knowledge")
def get_workspace_knowledge(id: str, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    statement = select(Block).where(Block.workspace_id == id).where(Block.type == "incident_knowledge")
    block = session.exec(statement).first()
    if not block:
        raise HTTPException(status_code=404, detail="No incident knowledge found for this workspace")
    return block.content

@router.post("/{id}/learn")
async def learn_workspace_incident(id: str, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Load incident summary block
    inc_stmt = select(Block).where(Block.workspace_id == id).where(Block.type == "incident_summary")
    inc_block = session.exec(inc_stmt).first()
    inc_dict = inc_block.content if inc_block else {
        "incident_title": "Payment Database Connection Failure",
        "summary": "Payment API unable to acquire database connections",
        "affected_services": ["payments-api"],
        "root_cause": "Database connection pool exhaustion",
        "confidence": 0.75,
        "current_status": "investigating"
    }

    # Load resolution block
    res_stmt = select(Block).where(Block.workspace_id == id).where(Block.type == "resolution")
    res_block = session.exec(res_stmt).first()
    res_dict = res_block.content if res_block else {
        "status": "monitoring",
        "completed_actions": ["Database connection pool limit increased"],
        "remaining_risks": ["Connection pooling leak under peak load"]
    }

    # 1. Embed incident
    embed_agent = EmbeddingAgent()
    embed_result = await embed_agent.embed_incident(
        incident_id=f"INC-{id[:4].upper()}",
        title=inc_dict.get("incident_title", ""),
        root_cause=inc_dict.get("root_cause", ""),
        services=inc_dict.get("affected_services", [])
    )

    # 2. Retrieve similar incidents
    retrieval_agent = IncidentRetrievalAgent()
    similar_inc_dict = await retrieval_agent.retrieve_similar_incidents(inc_dict)

    # 3. Analyze Similarity
    similarity_agent = SimilarityAgent()
    comparison_dict = await similarity_agent.compare_incidents(inc_dict, similar_inc_dict.get("similar_incidents", []))

    # 4. Learning Agent
    learn_agent = LearningAgent()
    recs_dict = await learn_agent.generate_recommendations(inc_dict, similar_inc_dict.get("similar_incidents", []), res_dict)

    # 5. Pattern Detection Agent
    pattern_agent = PatternDetectionAgent()
    patterns_dict = await pattern_agent.detect_patterns(inc_dict, similar_inc_dict.get("similar_incidents", []))

    # Helper function to save blocks
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

    # Persist all blocks in DB
    save_or_update_block("incident_similarity", similar_inc_dict)
    save_or_update_block("knowledge_search", comparison_dict)
    save_or_update_block("learning_recommendations", recs_dict)
    save_or_update_block("failure_patterns", patterns_dict)

    return {
        "similar_incidents": similar_inc_dict,
        "patterns": patterns_dict,
        "recommendations": recs_dict
    }

@router.get("/{id}/similar-incidents")
def get_workspace_similar_incidents(id: str, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    statement = select(Block).where(Block.workspace_id == id).where(Block.type == "incident_similarity")
    block = session.exec(statement).first()
    if not block:
        raise HTTPException(status_code=404, detail="No similar incidents found for this workspace")
    return block.content

@router.get("/{id}/recommendations")
def get_workspace_recommendations(id: str, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    statement = select(Block).where(Block.workspace_id == id).where(Block.type == "learning_recommendations")
    block = session.exec(statement).first()
    if not block:
        raise HTTPException(status_code=404, detail="No learning recommendations found for this workspace")
    return block.content

@router.get("/{id}/patterns")
def get_workspace_patterns(id: str, session: Session = Depends(get_session)):
    ws = session.get(Workspace, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    statement = select(Block).where(Block.workspace_id == id).where(Block.type == "failure_patterns")
    block = session.exec(statement).first()
    if not block:
        raise HTTPException(status_code=404, detail="No failure patterns found for this workspace")
    return block.content



