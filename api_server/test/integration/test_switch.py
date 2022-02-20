import json
import pytest

from src.interface_adapter.sql.model.models import  db
from src.interface_adapter.sql.model.models import Switch
from test.integration.resource import TEST_HEADERS, INVALID_IP, base_url


@pytest.fixture
def sample_switch():
    yield Switch(
        id=1,
        description='Switch',
        ip='192.168.102.2',
        communaute='communaute',
    )


@pytest.fixture
def client(sample_switch1):
    from .context import app
    from .conftest import prep_db, close_db
    with app.app.test_client() as c:
        prep_db(
            sample_switch1
        )
        yield c
        close_db()


def assert_switch_in_db(body):
    s = db.session()
    q = s.query(Switch)
    q = q.filter(Switch.ip == body["ip"])
    sw = q.one()
    assert sw.ip == body["ip"]
    assert sw.communaute == body["community"]
    assert sw.description == body["description"]


@pytest.mark.parametrize("test_ip", INVALID_IP)
def test_switch_post_invalid_ip(client, test_ip):
    sample_switch1 = {
        "description": "Test Switch",
        "ip": test_ip,
        "community": "myGreatCommunity"
    }
    r = client.post(
        "{}/switch/".format(base_url),
        data=json.dumps(sample_switch1),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert r.status_code == 400


def test_switch_post_valid(client):
    sample_switch1 = {
        "description": "Test Switch",
        "ip": "192.168.103.128",
        "community": "myGreatCommunity"
    }

    # Insert data to the database
    r = client.post(
        "{}/switch/".format(base_url),
        data=json.dumps(sample_switch1),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert r.status_code == 201
    assert_switch_in_db(sample_switch1)


def test_switch_get_all_invalid_limit(client):
    r = client.get(
        "{}/switch/?limit={}".format(base_url, -1),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_switch_get_all_limit(client):
    r = client.get(
        "{}/switch/?limit={}".format(base_url, 0),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    t = json.loads(r.data.decode('utf-8'))
    assert len(t) == 0


def test_switch_get_all(client):
    r = client.get(
        "{}/switch/".format(base_url),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    t = json.loads(r.data.decode('utf-8'))
    assert t
    assert len(t) == 1


def test_switch_get_existant_switch(client):
    r = client.get(
        "{}/switch/{}".format(base_url, 1),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    assert json.loads(r.data.decode('utf-8'))


def test_switch_get_non_existant_switch(client):
    r = client.get(
        "{}/switch/{}".format(base_url, 100000),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_switch_filter_by_term_ip(client):
    terms = "102.51"
    r = client.get(
        "{}/switch/?terms={}".format(base_url, terms),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.data.decode('utf-8'))
    assert result
    assert len(result) == 1


def test_switch_filter_by_term_desc(client):
    terms = "Switch"
    r = client.get(
        "{}/switch/?terms={}".format(base_url, terms),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.data.decode('utf-8'))
    assert result
    assert len(result) == 1


def test_switch_filter_by_term_nonexistant(client):
    terms = "HEYO"
    r = client.get(
        "{}/switch/?terms={}".format(base_url, terms),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.data.decode('utf-8'))
    assert not result


@pytest.mark.parametrize("test_ip", INVALID_IP)
def test_switch_update_switch_invalid_ip(client, test_ip):
    sample_switch1 = {
        "description": "Modified switch",
        "ip": test_ip,
        "community": "communityModified"
    }

    r = client.put(
        "{}/switch/{}".format(base_url, 1),
        data=json.dumps(sample_switch1),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert r.status_code == 400


def test_switch_update_existant_switch(client):
    sample_switch1 = {
        "description": "Modified switch",
        "ip": "192.168.103.132",
        "community": "communityModified"
    }

    r = client.put(
        "{}/switch/{}".format(base_url, 1),
        data=json.dumps(sample_switch1),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert r.status_code == 204
    assert_switch_in_db(sample_switch1)


def test_switch_update_non_existant_switch(client):
    sample_switch1 = {
        "description": "Modified switch",
        "ip": "192.168.103.132",
        "community": "communityModified"
    }

    r = client.put(
        "{}/switch/{}".format(base_url, 100000),
        data=json.dumps(sample_switch1),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert r.status_code == 404


def test_switch_delete_existant_switch(client):
    r = client.delete(
        "{}/switch/{}".format(base_url, 1),
        headers=TEST_HEADERS
    )
    assert r.status_code == 204
    s = db.session()
    q = s.query(Switch)
    q = q.filter(Switch.id == 1)

    assert not s.query(q.exists()).scalar()


def test_switch_delete_non_existant_switch(client):
    r = client.delete(
        "{}/switch/{}".format(base_url, 10000),
        headers=TEST_HEADERS
    )
    assert r.status_code == 404
