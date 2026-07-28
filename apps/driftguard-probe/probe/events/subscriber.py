"""Abstract Event Subscriber interfaces."""
from abc import ABC, abstractmethod
from typing import Optional
from .models import DomainEvent, EventType
from .bus import EventBus, get_event_bus


class EventSubscriber(ABC):
    """Abstract class for persistent listeners or logging exporters."""
    def __init__(self, bus: Optional[EventBus] = None, event_type: Optional[EventType] = None):
        self.bus = bus or get_event_bus()
        self.bus.subscribe(self.on_event, event_type)

    @abstractmethod
    async def on_event(self, event: DomainEvent) -> None:
        """Handle incoming event broadcast."""
        pass
