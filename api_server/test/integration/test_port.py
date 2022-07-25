import json

import pytest
from pytest_lazyfixture import lazy_fixture

from adh6.storage.sql.models import  Switch, db
from adh6.storage.sql.models import Port
from test.integration.resource import base_url, TEST_HEADERS


@pytest.fixture
def client(sample_port1,
            sample_port2,
            sample_room1,
            sample_member):
    from .context import app
    from .conftest import prep_db, close_db
    if app.app is None:
        return
    with app.app.test_client() as c:
        prep_db(
            sample_port1,
            sample_port2,
            sample_room1,
            sample_member
        )
        yield c
        close_db()


def assert_port_in_db(body):
    s = db.session()
    q = s.query(Port)
    q = q.filter(Port.numero == body["portNumber"])
    p = q.one()
    assert body["portNumber"] == p.numero
    assert body["room"] == p.chambre.id
    assert body["switchObj"] == p.switch.id

def test_port_get_filter_all(client):
    r = client.get(
        f"{base_url}/port/",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    switches = json.loads(r.data.decode())
    assert switches
    assert len(switches) == 2


@pytest.mark.parametrize(
    'sample_only', 
    [
        ("id"),
        ("portNumber"),
        ("oid"),
        ("switchObj"),
    ])
def test_port_search_with_only(client, sample_only: str):
    r = client.get(
        f'{base_url}/port/?only={sample_only}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 2
    assert len(set(sample_only.split(",") + ["__typename", "id"])) == len(set(response[0].keys()))


def test_member_search_with_unknown_only(client):
    sample_only = "azerty"
    r = client.get(
        f'{base_url}/port/?only={sample_only}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_member_filter_all_with_invalid_limit(client):
    r = client.get(
        '{}/member/?limit={}'.format(base_url, -1),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_member_filter_all_with_limit(client):
    r = client.get(
        '{}/member/?limit={}'.format(base_url, 1),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 1


def test_port_get_filter_all_with_invalid_limit(client):
    r = client.get(
        f"{base_url}/port/?limit={-1}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400

@pytest.mark.parametrize(
    'limit',
    [1, 2, 3]
)
def test_port_get_filter_all_with_limit(client, limit: int):
    r = client.get(
        f"{base_url}/port/?limit={limit}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    ports = json.loads(r.data.decode())
    assert ports
    assert len(ports) == (limit if limit <= 2 else 2)

@pytest.fixture
def sample_switch2_id(sample_switch2: Switch):
    yield sample_switch2.id

@pytest.fixture
def sample_port1_room_id(sample_port1: Port):
    yield sample_port1.chambre.id

@pytest.mark.parametrize(
    'filter_name,filter_value,quantity',
    [
        ('switchObj', lazy_fixture('sample_switch2_id'), 1),
        ('room', lazy_fixture('sample_port1_room_id'), 2),
        ('room', 4242, 0),
    ]
)
def test_port_get_filter_by_filter(client, filter_name, filter_value, quantity: int):
    r = client.get(
        f"{base_url}/port/?filter[{filter_name}]={filter_value}",
        headers=TEST_HEADERS
    )
    assert r.status_code == 200
    ports = json.loads(r.data.decode())
    assert len(ports) == quantity

@pytest.mark.parametrize(
    'term',
    [
        '1.2',
        '0/0/1'
    ]
)
def test_port_get_filter_by_term(client, term: str):
    r = client.get(
        f"{base_url}/port/?terms={term}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    ports = json.loads(r.data.decode())
    assert ports
    assert len(ports) == 1


def test_port_post_create_port_invalid_switch(client, sample_room1):
    body = {
        "room": sample_room1.id,
        "switchObj": 4242,
        "portNumber": "1/0/4",
        "oid": "10104"
    }

    r = client.post(
        "{}/port/".format(base_url),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_port_post_create_port_invalid_room(client, sample_switch1):
    body = {
        "room": 4242,
        "switchObj": sample_switch1.id,
        "portNumber": "1/0/4",
        "oid": "10104"
    }

    r = client.post(
        "{}/port/".format(base_url),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_port_post_create_port(client, sample_switch1, sample_room1):
    body = {
        "room": sample_room1.id,
        "switchObj": sample_switch1.id,
        "portNumber": "1/0/4",
        "oid": "10104"
    }

    r = client.post(
        "{}/port/".format(base_url),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 201


def test_port_get_existant_port(client, sample_port1):
    r = client.get(
        f"{base_url}/port/{sample_port1.id}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    switch = json.loads(r.data.decode())
    assert switch


def test_port_get_non_existant_port(client):
    r = client.get(
        f"{base_url}/port/{4242}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404

@pytest.fixture
def sample_ports1_id(sample_port1: Port):
    yield sample_port1.id

@pytest.mark.parametrize(
    'port_id,key,value,status_code',
    [
        (lazy_fixture('sample_ports1_id'), "switchObj", 999, 404),
        (4242, None, None, 404),
        (lazy_fixture('sample_ports1_id'), "portNumber", "1/2/3", 204),
    ]
)
def test_port_put_update_port(client, sample_switch1: Switch, sample_port1: Port, port_id: int, key: str, value, status_code: int):
    body = {
        "room": sample_port1.chambre.id,
        "oid": sample_port1.oid,
        "switchObj": sample_switch1.id,
        "portNumber": sample_port1.numero
    }

    if key is not None:
        body[key] = value

    r = client.put(
        f"{base_url}/port/{port_id}",
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == status_code
    if r.status_code == 204:
        assert_port_in_db(body)

@pytest.mark.parametrize(
    'port_id, status_code',
    [
        (lazy_fixture('sample_ports1_id'), 204), 
        (4242, 404)
    ]
)
def test_port_delete_port(client, port_id: int, status_code: int):
    r = client.delete(
        f"{base_url}/port/{port_id}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == status_code

    if status_code == 204:
        s = db.session()
        q = s.query(Port)
        q = q.filter(Port.id == port_id)
        assert not s.query(q.exists()).scalar()
