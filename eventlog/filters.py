from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Optional

from .models import Event


def filter_events(
    events: Iterable[Event],
    kind: Optional[str] = None,
    source: Optional[str] = None,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
) -> List[Event]:
    result = []
    for event in events:
        if kind is not None and event.kind != kind:
            continue
        if source is not None and event.source != source:
            continue
        if since is not None and event.created_at < since:
            continue
        if until is not None and event.created_at > until:
            continue
        result.append(event)
    return result
