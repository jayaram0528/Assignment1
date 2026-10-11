from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from .exporters import to_csv, to_jsonl
from .service import EventService
from .stats import bucket_counts, top_sources
from .storage import JsonFileStorage


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="eventlog")
    parser.add_argument("--db", default="events.json", help="path to the JSON store")
    sub = parser.add_subparsers(dest="command", required=True)

    rec = sub.add_parser("record", help="record a new event")
    rec.add_argument("kind")
    rec.add_argument("source")
    rec.add_argument("--payload", default="{}", help="JSON object")

    lst = sub.add_parser("list", help="list events")
    lst.add_argument("--kind")
    lst.add_argument("--source")
    lst.add_argument("--limit", type=int)

    stats = sub.add_parser("stats", help="show simple statistics")
    stats.add_argument("--granularity", default="hour", choices=["minute", "hour", "day"])

    exp = sub.add_parser("export", help="export all events")
    exp.add_argument("--format", default="csv", choices=["csv", "jsonl"])

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    service = EventService(JsonFileStorage(args.db))

    if args.command == "record":
        try:
            payload = json.loads(args.payload)
        except json.JSONDecodeError:
            print("payload must be valid JSON", file=sys.stderr)
            return 2
        if not isinstance(payload, dict):
            print("payload must be a JSON object", file=sys.stderr)
            return 2
        event = service.record(args.kind, args.source, payload)
        print(event.id)
        return 0

    if args.command == "list":
        for event in service.list(kind=args.kind, source=args.source, limit=args.limit):
            print(f"{event.id}\t{event.kind}\t{event.source}\t{event.created_at.isoformat()}")
        return 0

    if args.command == "stats":
        events = service.list()
        print("by kind:", service.count_by_kind())
        print("top sources:", top_sources(events))
        for bucket, count in bucket_counts(events, args.granularity).items():
            print(f"{bucket.isoformat()}\t{count}")
        return 0

    if args.command == "export":
        events = service.list()
        sys.stdout.write(to_csv(events) if args.format == "csv" else to_jsonl(events))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
