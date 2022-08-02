import pytest
from test.integration.resource import TEST_HEADERS, TEST_HEADERS_SAMPLE, base_url as host_url

base_url = f'{host_url}/profile'


@pytest.fixture
def client(sample_member):
    from .context import app
    from .conftest import prep_db, close_db
    if app.app is None:
        return
    with app.app.test_client() as c:
        prep_db(sample_member)
        yield c
        close_db()


def test_profile_admin(client):
    r = client.get(
        base_url,
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200


def test_profile_user(client):
    r = client.get(
        base_url,
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 200
