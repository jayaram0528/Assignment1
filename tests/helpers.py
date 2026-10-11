from datetime import datetime, timezone

from eventlog.models import Event


def make_event(event_id, kind="login", source="web", minutes=0, hour=12, payload=None):
    return Event(
        id=event_id,
        kind=kind,
        source=source,
        payload=payload or {},
        created_at=datetime(2026, 1, 1, hour, minutes, 0, tzinfo=timezone.utc),
    )
