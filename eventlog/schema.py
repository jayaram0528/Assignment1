from __future__ import annotations

from typing import Any, Dict, Optional


class SchemaError(ValueError):
    pass


def _matches(value: Any, expected: type) -> bool:
    # bool is a subclass of int, but a True/False is never a valid count or id
    if expected is int and isinstance(value, bool):
        return False
    if expected is float and isinstance(value, int) and not isinstance(value, bool):
        return True
    return isinstance(value, expected)


class SchemaRegistry:
    """Optional per-kind payload validation. Kinds without a schema are accepted as-is."""

    def __init__(self) -> None:
        self._schemas: Dict[str, Dict[str, Any]] = {}

    def register(
        self,
        kind: str,
        required: Dict[str, type],
        optional: Optional[Dict[str, type]] = None,
        allow_extra: bool = True,
    ) -> None:
        self._schemas[kind] = {
            "required": dict(required),
            "optional": dict(optional or {}),
            "allow_extra": allow_extra,
        }

    def has_schema(self, kind: str) -> bool:
        return kind in self._schemas

    def validate(self, kind: str, payload: Dict[str, Any]) -> None:
        schema = self._schemas.get(kind)
        if schema is None:
            return

        for key, expected in schema["required"].items():
            if key not in payload:
                raise SchemaError(f"{kind}: missing required field '{key}'")
            if not _matches(payload[key], expected):
                raise SchemaError(f"{kind}: field '{key}' must be {expected.__name__}")

        for key, expected in schema["optional"].items():
            if key in payload and not _matches(payload[key], expected):
                raise SchemaError(f"{kind}: field '{key}' must be {expected.__name__}")

        if not schema["allow_extra"]:
            known = set(schema["required"]) | set(schema["optional"])
            extra = set(payload) - known
            if extra:
                raise SchemaError(f"{kind}: unexpected fields {sorted(extra)}")
