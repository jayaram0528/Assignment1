from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta
from typing import Dict, Iterable, List, Tuple

from .models import Event

_GRANULARITIES = ("minute", "hour", "day")


def _truncate(moment: datetime, granularity: str) -> datetime:
    if granularity == "minute":
        return moment.replace(second=0, microsecond=0)
    if granularity == "hour":
        return moment.replace(minute=0, second=0, microsecond=0)
    if granularity == "day":
        return moment.replace(hour=0, minute=0, second=0, microsecond=0)
    raise ValueError(f"granularity must be one of {_GRANULARITIES}")


def bucket_counts(events: Iterable[Event], granularity: str = "hour") -> Dict[datetime, int]:
    if granularity not in _GRANULARITIES:
        raise ValueError(f"granularity must be one of {_GRANULARITIES}")
    counts: Counter = Counter()
    for event in events:
        counts[_truncate(event.created_at, granularity)] += 1
    return dict(sorted(counts.items()))


def top_sources(events: Iterable[Event], n: int = 3) -> List[Tuple[str, int]]:
    """Most active sources first; ties are broken alphabetically so output is stable."""
    counts = Counter(event.source for event in events)
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return ordered[:n]


def rate_per_minute(events: Iterable[Event], window_minutes: int, now: datetime) -> float:
    if window_minutes <= 0:
        raise ValueError("window_minutes must be positive")
    start = now - timedelta(minutes=window_minutes)
    in_window = sum(1 for e in events if start <= e.created_at <= now)
    return in_window / window_minutes
