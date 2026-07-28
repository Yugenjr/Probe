"""Event publishing wrapper utility."""
import uuid
from typing import Any, Dict, Optional
from .models import DomainEvent, EventType
from .bus import EventBus, get_event_bus


class EventPublisher:
    """Utility helper allowing modules to easily generate and broadcast domain events."""
    def __init__(self, source_module: str, bus: Optional[EventBus] = None):
        self.source_module = source_module
        self.bus = bus or get_event_bus()

    async def emit(
        self,
        event_type: EventType,
        investigation_id: Optional[str] = None,
        **attributes: Any,
    ) -> DomainEvent:
        """Create structured DomainEvent and publish over bus."""
        event = DomainEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            investigation_id=investigation_id,
            source_module=self.source_module,
            attributes=attributes,
        )
        await self.bus.publish(event)
        return event
