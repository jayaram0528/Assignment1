from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Protocol

from .models import Event


class Storage(Protocol):
    def add(self, event: Event) -> None: ...
    def get(self, event_id: int) -> Optional[Event]: ...
    def all(self) -> List[Event]: ...
    def delete(self, event_id: int) -> bool: ...
    def next_id(self) -> int: ...


class InMemoryStorage:
    def __init__(self) -> None:
        self._events: Dict[int, Event] = {}
        self._counter = 0

    def add(self, event: Event) -> None:
        self._events[event.id] = event

    def get(self, event_id: int) -> Optional[Event]:
        return self._events.get(event_id)

    def all(self) -> List[Event]:
        return sorted(self._events.values(), key=lambda e: e.id)

    def delete(self, event_id: int) -> bool:
        return self._events.pop(event_id, None) is not None

    def next_id(self) -> int:
        self._counter += 1
        return self._counter


class JsonFileStorage(InMemoryStorage):
    """In-memory storage that persists to a JSON file on every write."""

    def __init__(self, path: str | Path) -> None:
        super().__init__()
        self._path = Path(path)
        if self._path.exists():
            self._load()

    def _load(self) -> None:
        raw = json.loads(self._path.read_text() or "[]")
        for item in raw:
            event = Event.from_dict(item)
            self._events[event.id] = event
            self._counter = max(self._counter, event.id)

    def _flush(self) -> None:
        data = [e.to_dict() for e in self.all()]
        self._path.write_text(json.dumps(data, indent=2))

    def add(self, event: Event) -> None:
        super().add(event)
        self._flush()

    def delete(self, event_id: int) -> bool:
        removed = super().delete(event_id)
        if removed:
            self._flush()
        return removed
