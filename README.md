# eventlog

A small Python library for recording and querying events, with pluggable storage backends.

## Layout

- `eventlog/models.py` – the `Event` dataclass
- `eventlog/storage.py` – `InMemoryStorage` and `JsonFileStorage`
- `eventlog/filters.py` – filtering by kind, source and time range
- `eventlog/schema.py` – optional per-kind payload validation
- `eventlog/hooks.py` – `recorded` / `deleted` subscriptions
- `eventlog/stats.py` – time buckets, top sources, event rate
- `eventlog/retention.py` – age and per-kind retention policies
- `eventlog/exporters.py` – CSV and JSON Lines export
- `eventlog/cli.py` – command line interface
- `eventlog/service.py` – `EventService`, the public API

## Usage

```python
from eventlog import EventService, InMemoryStorage, RetentionPolicy

service = EventService(InMemoryStorage())
service.schemas.register("purchase", required={"amount": float, "user": str})
service.record("purchase", "shop", {"amount": 9.5, "user": "ann"})
print(service.list(kind="purchase"))
service.apply_retention(RetentionPolicy(max_per_kind=100))
```

CLI:

```bash
python -m eventlog.cli --db events.json record login web --payload '{"user": "ann"}'
python -m eventlog.cli --db events.json list --kind login
python -m eventlog.cli --db events.json export --format csv
```

## Tests

```bash
pip install pytest
pytest
```

## License

MIT
