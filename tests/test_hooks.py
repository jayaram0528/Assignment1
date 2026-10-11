from eventlog import EventService, HookBus, InMemoryStorage


def test_recorded_hook_fires():
    seen = []
    service = EventService(InMemoryStorage())
    service.hooks.subscribe("recorded", lambda e: seen.append(e.kind))
    service.record("login", "web")
    assert seen == ["login"]


def test_deleted_hook_receives_event():
    seen = []
    service = EventService(InMemoryStorage())
    event = service.record("login", "web")
    service.hooks.subscribe("deleted", lambda e: seen.append(e.id))
    service.delete(event.id)
    assert seen == [event.id]


def test_failing_handler_does_not_block_others():
    bus = HookBus()
    calls = []

    def bad(_):
        raise RuntimeError("boom")

    bus.subscribe("recorded", bad)
    bus.subscribe("recorded", lambda e: calls.append(e.id))

    service = EventService(InMemoryStorage(), hooks=bus)
    service.record("a", "x")
    assert calls == [1]
    assert len(bus.errors) == 1


def test_unsubscribe():
    bus = HookBus()
    handler = lambda e: None  # noqa: E731
    bus.subscribe("recorded", handler)
    assert bus.unsubscribe("recorded", handler) is True
    assert bus.unsubscribe("recorded", handler) is False
