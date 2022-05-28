from test.integration.resource import TEST_HEADERS, base_url


def test_good_health():
    from .context import app
    if app.app is None:
        return
    with app.app.test_client() as c:
        r = c.get(
            f'{base_url}/health',
            headers=TEST_HEADERS,
        )
        assert r.status_code == 200
