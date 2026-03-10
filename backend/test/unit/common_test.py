def test_app_exists():
    """Test that the FastAPI app can be imported."""
    from adh6.main import app

    assert app is not None
    assert hasattr(app, "routes")
