"""Minimal test to diagnose hanging issue."""

import pytest


def test_basic():
    """Test that doesn't use any fixtures."""
    assert 1 + 1 == 2


@pytest.fixture
def simple_app():
    from .context import app

    return app


def test_with_app(simple_app):
    """Test that only uses app fixture."""
    assert simple_app is not None


@pytest.fixture
def simple_client(simple_app):
    from fastapi.testclient import TestClient

    with TestClient(simple_app) as client:
        yield client


def test_with_client(simple_client):
    """Test that uses test client."""
    r = simple_client.get("/health")
    # Even if endpoint doesn't exist, should get some response
    assert r is not None
