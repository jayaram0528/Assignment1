from __future__ import annotations

import csv
import io
import json
from typing import Iterable

from .models import Event

CSV_COLUMNS = ["id", "kind", "source", "created_at", "payload"]


def to_csv(events: Iterable[Event]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(CSV_COLUMNS)
    for event in events:
        writer.writerow(
            [
                event.id,
                event.kind,
                event.source,
                event.created_at.isoformat(),
                json.dumps(event.payload, sort_keys=True),
            ]
        )
    return buffer.getvalue()


def to_jsonl(events: Iterable[Event]) -> str:
    lines = [json.dumps(event.to_dict(), sort_keys=True) for event in events]
    return "\n".join(lines) + ("\n" if lines else "")
