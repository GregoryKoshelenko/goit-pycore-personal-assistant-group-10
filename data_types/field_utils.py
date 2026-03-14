"""Helpers to normalize values through Field subclasses (always use field `.value`)."""

from typing import TypeVar

from data_types.field_base import Field

F = TypeVar("F", bound=type[Field])


def normalize_optional(raw: object | None, field_cls: F) -> object | None:
    """None stays None; otherwise validate via field_cls and return ``instance.value``."""
    if raw is None:
        return None
    if isinstance(raw, field_cls):
        return raw.value
    return field_cls(raw).value


def normalize_required(raw: object, field_cls: F) -> object:
    """Validate via field_cls; return ``instance.value`` (str, datetime, etc.)."""
    if isinstance(raw, field_cls):
        return raw.value
    return field_cls(raw).value
