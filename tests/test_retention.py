from datetime import datetime, timedelta, timezone

import pytest

from eventlog import EventService, InMemoryStorage, RetentionPolicy
from eventlog.retention import select_expired
from tests.helpers import make_event

NOW = datetime(2026, 1, 1, 13, 0, tzinfo=timezone.utc)


def test_max_age_selects_old_events():
    events = [make_event(1, hour=9), make_event(2, hour=12, minutes=30)]
    expired = select_expired(events, RetentionPolicy(max_age=timedelta(hours=2)), NOW)
    assert expired == [1]


def test_max_per_kind_keeps_newest():
    events = [make_event(i, kind="a", minutes=i) for i in range(1, 5)]
    expired = select_expired(events, RetentionPolicy(max_per_kind=2), NOW)
    assert expired == [1, 2]


def test_max_per_kind_tie_uses_id():
    events = [make_event(1, kind="a"), make_event(2, kind="a")]
    assert select_expired(events, RetentionPolicy(max_per_kind=1), NOW) == [1]


def test_policies_combine_without_duplicates():
    events = [make_event(1, kind="a", hour=8), make_event(2, kind="a", hour=12, minutes=50)]
    policy = RetentionPolicy(max_age=timedelta(hours=1), max_per_kind=1)
    assert select_expired(events, policy, NOW) == [1]


def test_empty_policy_removes_nothing():
    assert select_expired([make_event(1)], RetentionPolicy(), NOW) == []


def test_negative_max_per_kind_rejected():
    with pytest.raises(ValueError):
        RetentionPolicy(max_per_kind=-1)


def test_service_apply_retention_removes_and_counts():
    storage = InMemoryStorage()
    service = EventService(storage)
    for i in range(4):
        service.record("a", "web")
    removed = service.apply_retention(RetentionPolicy(max_per_kind=1))
    assert removed == 3
    assert [e.id for e in service.list()] == [4]
