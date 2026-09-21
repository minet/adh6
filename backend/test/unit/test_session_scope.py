"""The request's transaction must be committed before its response is sent.

`get_session` commits when its dependency exits. With FastAPI's default "request" scope, that exit
runs after the response is sent: a client could receive 204 for a PATCH and read the old row on its
very next request. Payment did exactly that, PATCH then POST validate, and a paid membership was
refused as PENDING_PAYMENT_INITIAL.

Every use must share the same scope too: the scope is part of the dependency cache key, so mixing
them would give the authentication and the route two different sessions.
"""

from adh6.database import get_session
from adh6.main import app
from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute


def _session_dependants(dependant: Dependant, path: str):
    for sub in dependant.dependencies:
        if sub.call is get_session:
            yield path, sub
        yield from _session_dependants(sub, path)


def test_every_session_is_committed_before_the_response():
    found = [
        (path, sub)
        for route in app.routes
        if isinstance(route, APIRoute)
        for path, sub in _session_dependants(route.dependant, f"{sorted(route.methods)} {route.path}")
    ]
    assert found, "no route uses get_session: the test no longer checks anything"
    late = sorted({path for path, sub in found if sub.computed_scope != "function"})
    assert not late, f"get_session commits after the response on: {late}"
