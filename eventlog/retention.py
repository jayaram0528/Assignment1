from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable, List, Optional, Set

from .models import Event


@dataclass
class RetentionPolicy:
    max_age: Optional[timedelta] = None
    max_per_kind: Optional[int] = None

    def __post_init__(self) -> None:
        if self.max_per_kind is not None and self.max_per_kind < 0:
            raise ValueError("max_per_kind cannot be negative")


def select_expired(
    events: Iterable[Event],
    policy: RetentionPolicy,
    now: Optional[datetime] = None,
) -> List[int]:
    """Return ids of events the policy says should be removed (sorted)."""
    now = now or datetime.now(timezone.utc)
    events = list(events)
    expired: Set[int] = set()

    if policy.max_age is not None:
        cutoff = now - policy.max_age
        expired.update(e.id for e in events if e.created_at < cutoff)

    if policy.max_per_kind is not None:
        by_kind: Dict[str, List[Event]] = {}
        for event in events:
            by_kind.setdefault(event.kind, []).append(event)
        for group in by_kind.values():
            # newest first; id breaks ties between identical timestamps
            group.sort(key=lambda e: (e.created_at, e.id), reverse=True)
            expired.update(e.id for e in group[policy.max_per_kind:])

    return sorted(expired)
