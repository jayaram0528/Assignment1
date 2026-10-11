from eventlog import EventService, JsonFileStorage


def test_json_storage_persists_across_instances(tmp_path):
    path = tmp_path / "events.json"
    first = EventService(JsonFileStorage(path))
    first.record("login", "web", {"user": "ann"})

    second = EventService(JsonFileStorage(path))
    events = second.list()
    assert len(events) == 1
    assert events[0].payload == {"user": "ann"}


def test_json_storage_continues_ids_after_reload(tmp_path):
    path = tmp_path / "events.json"
    EventService(JsonFileStorage(path)).record("a", "x")
    service = EventService(JsonFileStorage(path))
    assert service.record("b", "x").id == 2
