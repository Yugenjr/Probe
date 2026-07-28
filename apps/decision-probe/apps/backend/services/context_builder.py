from sqlmodel import Session, select
from storage.models import Workspace, Block, ProviderSetting
from .models import ReasoningContext
from datetime import datetime, timezone
import json

class ContextBuilder:
    def __init__(self, session: Session):
        self.session = session

    def build(self, workspace_id: str, user_prompt: str) -> ReasoningContext:
        """
        Gathers all the raw materials needed for reasoning and returns
        a highly structured ReasoningContext object.
        """
        # 1. Fetch Workspace
        ws = self.session.get(Workspace, workspace_id)
        if not ws:
            raise ValueError(f"Workspace {workspace_id} not found.")

        # 2. Fetch Blocks
        blocks = self.session.exec(
            select(Block).where(Block.workspace_id == workspace_id).order_by(Block.order)
        ).all()

        serialized_blocks = [
            {"id": b.id, "type": b.type, "order": b.order, "content": b.content} 
            for b in blocks
        ]

        # 3. Fetch Settings
        providers = self.session.exec(select(ProviderSetting)).all()
        settings = {p.id: {"enabled": p.enabled, "status": p.status} for p in providers}

        # 4. Filter block history for context
        # (Incident blocks represent user prompts/history)
        conversation = [
            b for b in serialized_blocks if b["type"] in ["incident"]
        ]

        # 5. Extract specific block types for the new expanded ReasoningContext
        timeline = [b for b in serialized_blocks if b["type"] == "timeline"]
        current_decisions = [b for b in serialized_blocks if b["type"] == "decision"]
        
        # 6. Build Context
        context = ReasoningContext(
            workspace_id=workspace_id,
            workspace_title=ws.title,
            workspace_description=ws.metadata.get("description", "") if isinstance(ws.metadata, dict) else "",
            user_prompt=user_prompt,
            timestamp=datetime.now(timezone.utc),
            blocks=serialized_blocks,
            conversation=conversation,
            settings=settings,
            provider_configuration=settings,
            timeline=timeline,
            current_decisions=current_decisions
        )

        return context
