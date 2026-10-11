import pytest

from eventlog import EventService, InMemoryStorage
from eventlog.service import EventNotFound


@pytest.fixture
def service():
    return EventService(InMemoryStorage())


def test_record_assigns_incrementing_ids(service):
    a = service.record("login", "web")
    b = service.record("logout", "web")
    assert (a.id, b.id) == (1, 2)


def test_record_requires_kind_and_source(service):
    with pytest.raises(ValueError):
        service.record("", "web")


def test_get_missing_raises(service):
    with pytest.raises(EventNotFound):
        service.get(99)


def test_list_filters_by_kind_and_source(service):
    service.record("login", "web")
    service.record("login", "mobile")
    service.record("logout", "web")
    assert len(service.list(kind="login")) == 2
    assert len(service.list(kind="login", source="web")) == 1


def test_list_limit(service):
    for _ in range(5):
        service.record("tick", "cron")
    assert len(service.list(limit=3)) == 3


def test_delete(service):
    event = service.record("login", "web")
    service.delete(event.id)
    with pytest.raises(EventNotFound):
        service.get(event.id)


def test_count_by_kind(service):
    service.record("a", "x")
    service.record("a", "x")
    service.record("b", "x")
    assert service.count_by_kind() == {"a": 2, "b": 1}
