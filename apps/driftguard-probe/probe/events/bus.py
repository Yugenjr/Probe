"""Async pub/sub Event Bus implementation."""
import asyncio
import logging
from typing import Any, Callable, Coroutine, Dict, List, Set
from .models import DomainEvent, EventType

logger = logging.getLogger(__name__)

EventCallback = Callable[[DomainEvent], Coroutine[Any, Any, None]]


class EventBus:
    """Asynchronous memory event broker decoupling multi-agent notifications."""
    def __init__(self):
        self._subscribers: Dict[EventType, List[EventCallback]] = {}
        self._global_subscribers: List[EventCallback] = []

    def subscribe(self, callback: EventCallback, event_type: EventType = None) -> None:
        """Register an async callback handler for specific or all events."""
        if event_type is None:
            self._global_subscribers.append(callback)
        else:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(callback)

    async def publish(self, event: DomainEvent) -> None:
        """Broadcast event to all relevant subscribed listeners asynchronously."""
        logger.debug("Publishing Event [%s] from %s", event.event_type.value, event.source_module)
        handlers = self._global_subscribers + self._subscribers.get(event.event_type, [])
        if not handlers:
            return

        tasks = [handler(event) for handler in handlers]
        # TODO: Implementation pending for robust task isolation and dead-letter queue recovery
        await asyncio.gather(*tasks, return_exceptions=True)


_global_bus = EventBus()


def get_event_bus() -> EventBus:
    """Acquire global event bus instance."""
    return _global_bus
