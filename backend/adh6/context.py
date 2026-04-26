"""Compatibility auth context helpers.

Legacy managers/tests still import ``adh6.context`` to retrieve current user/roles.
FastAPI code paths should prefer request-scoped auth via ``adh6.security``.
"""

from __future__ import annotations

from contextvars import ContextVar

_current_user: ContextVar[int | None] = ContextVar("adh6_current_user", default=None)
_current_roles: ContextVar[list[str]] = ContextVar("adh6_current_roles", default=[])
_current_api_key_id: ContextVar[int | None] = ContextVar("adh6_current_api_key_id", default=None)


def get_user() -> int | None:
    """Return the current user id for legacy code paths."""
    return _current_user.get()


def get_roles() -> list[str]:
    """Return the current role list for legacy code paths."""
    return _current_roles.get()


def get_api_key_id() -> int | None:
    """Return the current API key id, if the request was authenticated via API key."""
    return _current_api_key_id.get()


def set_user(user_id: int | None) -> None:
    """Set current user id in context."""
    _current_user.set(user_id)


def set_roles(roles: list[str]) -> None:
    """Set current role list in context."""
    _current_roles.set(roles)


def set_api_key_id(api_key_id: int | None) -> None:
    """Set current API key id in context."""
    _current_api_key_id.set(api_key_id)
