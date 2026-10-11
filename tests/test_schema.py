import pytest

from eventlog import EventService, InMemoryStorage, SchemaError, SchemaRegistry


@pytest.fixture
def registry():
    reg = SchemaRegistry()
    reg.register("purchase", required={"amount": float, "user": str}, optional={"note": str})
    return reg


def test_unregistered_kind_is_accepted(registry):
    registry.validate("anything", {"whatever": 1})


def test_missing_required_field(registry):
    with pytest.raises(SchemaError):
        registry.validate("purchase", {"user": "ann"})


def test_wrong_type(registry):
    with pytest.raises(SchemaError):
        registry.validate("purchase", {"amount": "10", "user": "ann"})


def test_int_is_accepted_for_float(registry):
    registry.validate("purchase", {"amount": 10, "user": "ann"})


def test_bool_is_rejected_for_int():
    reg = SchemaRegistry()
    reg.register("count", required={"n": int})
    with pytest.raises(SchemaError):
        reg.validate("count", {"n": True})


def test_optional_field_type_checked(registry):
    with pytest.raises(SchemaError):
        registry.validate("purchase", {"amount": 1.0, "user": "ann", "note": 5})


def test_disallow_extra_fields():
    reg = SchemaRegistry()
    reg.register("strict", required={"a": int}, allow_extra=False)
    with pytest.raises(SchemaError):
        reg.validate("strict", {"a": 1, "b": 2})


def test_service_rejects_invalid_payload(registry):
    service = EventService(InMemoryStorage(), schemas=registry)
    with pytest.raises(SchemaError):
        service.record("purchase", "shop", {"user": "ann"})
    assert service.list() == []
