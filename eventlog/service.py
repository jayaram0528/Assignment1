from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from .filters import filter_events
from .hooks import HookBus
from .models import Event
from .retention import RetentionPolicy, select_expired
from .schema import SchemaRegistry
from .storage import Storage


class EventNotFound(KeyError):
    pass


class EventService:
    def __init__(
        self,
        storage: Storage,
        schemas: Optional[SchemaRegistry] = None,
        hooks: Optional[HookBus] = None,
    ) -> None:
        self._storage = storage
        self.schemas = schemas or SchemaRegistry()
        self.hooks = hooks or HookBus()

    def record(self, kind: str, source: str, payload: Optional[Dict[str, Any]] = None) -> Event:
        if not kind or not source:
            raise ValueError("kind and source are required")
        payload = payload or {}
        self.schemas.validate(kind, payload)
        event = Event(
            id=self._storage.next_id(),
            kind=kind,
            source=source,
            payload=payload,
        )
        self._storage.add(event)
        self.hooks.emit("recorded", event)
        return event

    def get(self, event_id: int) -> Event:
        event = self._storage.get(event_id)
        if event is None:
            raise EventNotFound(event_id)
        return event

    def list(
        self,
        kind: Optional[str] = None,
        source: Optional[str] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[Event]:
        events = filter_events(self._storage.all(), kind, source, since, until)
        return events[:limit] if limit is not None else events

    def delete(self, event_id: int) -> None:
        event = self.get(event_id)
        self._storage.delete(event_id)
        self.hooks.emit("deleted", event)

    def count_by_kind(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for event in self._storage.all():
            counts[event.kind] = counts.get(event.kind, 0) + 1
        return counts

    def apply_retention(self, policy: RetentionPolicy, now: Optional[datetime] = None) -> int:
        """Delete events the policy marks as expired and return how many were removed."""
        removed = 0
        for event_id in select_expired(self._storage.all(), policy, now):
            self.delete(event_id)
            removed += 1
        return removed
