from datetime import datetime, timezone

import pytest

from eventlog.stats import bucket_counts, rate_per_minute, top_sources
from tests.helpers import make_event


def test_bucket_counts_by_hour():
    events = [make_event(1, hour=10), make_event(2, hour=10, minutes=30), make_event(3, hour=11)]
    counts = bucket_counts(events, "hour")
    assert list(counts.values()) == [2, 1]


def test_bucket_counts_by_day_merges_hours():
    events = [make_event(1, hour=1), make_event(2, hour=23)]
    assert list(bucket_counts(events, "day").values()) == [2]


def test_bucket_counts_invalid_granularity():
    with pytest.raises(ValueError):
        bucket_counts([], "week")


def test_top_sources_ties_are_alphabetical():
    events = [make_event(1, source="b"), make_event(2, source="a"), make_event(3, source="c")]
    assert top_sources(events, 2) == [("a", 1), ("b", 1)]


def test_top_sources_orders_by_count():
    events = [make_event(i, source="web") for i in range(3)] + [make_event(9, source="app")]
    assert top_sources(events, 1) == [("web", 3)]


def test_rate_per_minute():
    now = datetime(2026, 1, 1, 12, 10, tzinfo=timezone.utc)
    events = [make_event(1, minutes=5), make_event(2, minutes=8), make_event(3, minutes=0)]
    assert rate_per_minute(events, 5, now) == pytest.approx(2 / 5)


def test_rate_requires_positive_window():
    with pytest.raises(ValueError):
        rate_per_minute([], 0, datetime.now(timezone.utc))
