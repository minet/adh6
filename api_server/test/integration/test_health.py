from test.integration.resource import TEST_HEADERS, TEST_HEADERS_API_KEY_ADMIN, TEST_HEADERS_SAMPLE, base_url as host_url


base_url = f'{host_url}/health'


def test_good_health(client):
    r = client.get(
        f'{base_url}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200


def test_good_health_api_key(client):
    r = client.get(
        f'{base_url}',
        headers=TEST_HEADERS_API_KEY_ADMIN,
    )
    assert r.status_code == 200


def test_good_health_unauthorized(client):
    r = client.get(
        f'{base_url}',
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403
