from pydantic import BaseModel, ValidationError
from typing import List, Dict, Any, Optional
from sqlmodel import Session, select
from storage.models import Block
import json
import logging

logger = logging.getLogger(__name__)

class PatchPayload(BaseModel):
    type: str
    content: Dict[str, Any]

class PatchOperation(BaseModel):
    op: str
    target_id: Optional[str] = None
    payload: PatchPayload

class PatchBuilder:
    def __init__(self, session: Session):
        self.session = session

    def apply_and_yield_patches(self, workspace_id: str, raw_json: str):
        """
        Validates the raw JSON from the LLM.
        Applies operations to the database.
        Yields SSE strings for the frontend.
        """
        try:
            # We expect the LLM to return a list of operations
            data = json.loads(raw_json)
            if not isinstance(data, list):
                # Attempt to wrap it if it returned a single dict
                data = [data]
                
            operations = []
            for item in data:
                try:
                    op = PatchOperation(**item)
                    operations.append(op)
                except ValidationError as e:
                    logger.warning(f"Invalid patch operation: {e}")
                    
            for op in operations:
                if op.op == 'append_block':
                    # Calculate next order
                    blocks_count = self.session.exec(select(Block).where(Block.workspace_id == workspace_id)).all()
                    order = len(blocks_count)
                    
                    block = Block(
                        workspace_id=workspace_id,
                        type=op.payload.type,
                        order=order,
                        content=op.payload.content
                    )
                    self.session.add(block)
                    self.session.commit()
                    self.session.refresh(block)
                    
                    # Yield validated SSE
                    yield f"data: {json.dumps({'type': 'PatchOperation', 'operations': [{'op': 'append_block', 'target_id': workspace_id, 'payload': {'id': block.id, 'type': block.type, 'order': block.order, 'content': block.content}}]})}\n\n"
                
                # Further operations (update, delete) could be handled here
                
        except json.JSONDecodeError:
            logger.error("LLM returned malformed JSON.")
            yield f"data: {json.dumps({'type': 'error', 'content': 'LLM returned malformed JSON.'})}\n\n"

    def apply_operations(self, workspace_id: str, operations: list):
        """
        Applies pre-validated Pydantic operations directly to the DB without yielding SSE.
        """
        for op in operations:
            if op.op == 'append_block':
                blocks_count = self.session.exec(select(Block).where(Block.workspace_id == workspace_id)).all()
                order = len(blocks_count)
                
                block = Block(
                    workspace_id=workspace_id,
                    type=op.payload.type,
                    order=order,
                    content=op.payload.content
                )
                self.session.add(block)
                self.session.commit()
                self.session.refresh(block)
            
            elif op.op == 'update_block':
                # Simplified update mechanism for existing blocks
                if op.target_id:
                    block = self.session.get(Block, op.target_id)
                    if block:
                        block.content = op.payload.content
                        self.session.commit()
            
            elif op.op == 'delete_block':
                if op.target_id:
                    block = self.session.get(Block, op.target_id)
                    if block:
                        self.session.delete(block)
                        self.session.commit()
