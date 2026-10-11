from __future__ import annotations

from typing import Callable, Dict, List, Tuple

from .models import Event

Handler = Callable[[Event], None]


class HookBus:
    """Very small pub/sub. A failing handler never blocks the others."""

    def __init__(self) -> None:
        self._handlers: Dict[str, List[Handler]] = {}
        self.errors: List[Tuple[str, Exception]] = []

    def subscribe(self, topic: str, handler: Handler) -> None:
        self._handlers.setdefault(topic, []).append(handler)

    def unsubscribe(self, topic: str, handler: Handler) -> bool:
        handlers = self._handlers.get(topic, [])
        if handler in handlers:
            handlers.remove(handler)
            return True
        return False

    def emit(self, topic: str, event: Event) -> int:
        """Call every handler for the topic, return how many succeeded."""
        succeeded = 0
        for handler in list(self._handlers.get(topic, [])):
            try:
                handler(event)
                succeeded += 1
            except Exception as exc:  # noqa: BLE001
                self.errors.append((topic, exc))
        return succeeded
