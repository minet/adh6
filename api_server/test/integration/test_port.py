import json
from typing import Optional

import pytest
from pytest_lazyfixture import lazy_fixture

from src.interface_adapter.sql.model.models import  Switch, db
from src.interface_adapter.sql.model.models import Port
from test.integration.resource import TEST_HEADERS_API_KEY, TEST_HEADERS_SAMPLE, base_url, TEST_HEADERS


@pytest.fixture
def client(sample_port1,
            sample_port2,
            sample_room1,
            sample_member):
    from .context import app
    from .conftest import prep_db, close_db
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

@pytest.mark.parametrize(
    'headers, status_code',
    [
        (TEST_HEADERS, 200),
        (TEST_HEADERS_API_KEY, 200),
        (TEST_HEADERS_SAMPLE, 403),
    ]
)
def test_port_get_filter_all(client, headers, status_code: int):
    r = client.get(
        f"{base_url}/port/",
        headers=headers,
    )
    assert r.status_code == status_code
    if status_code != 200:
        switches = json.loads(r.data.decode())
        assert switches
        assert len(switches) == 2


@pytest.mark.parametrize(
    'headers, status_code',
    [
        (TEST_HEADERS, 400),
        (TEST_HEADERS_API_KEY, 400),
        (TEST_HEADERS_SAMPLE, 403),
    ]
)
def test_port_get_filter_all_with_invalid_limit(client, headers, status_code):
    r = client.get(
        f"{base_url}/port/?limit={-1}",
        headers=headers,
    )
    assert r.status_code == status_code

@pytest.mark.parametrize(
    'headers, status_code',
    [
        (TEST_HEADERS, 200),
        (TEST_HEADERS_API_KEY, 200),
        (TEST_HEADERS_SAMPLE, 403),
    ]
)
@pytest.mark.parametrize(
    'limit',
    [1, 2, 3]
)
def test_port_get_filter_all_with_limit(client, limit: int, headers, status_code: int):
    r = client.get(
        f"{base_url}/port/?limit={limit}",
        headers=headers,
    )
    assert r.status_code == status_code
    if status_code != 403:
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
    'headers, status_code',
    [
        (TEST_HEADERS, 200),
        (TEST_HEADERS_API_KEY, 200),
        (TEST_HEADERS_SAMPLE, 403),
    ]
)
@pytest.mark.parametrize(
    'filter_name,filter_value,quantity',
    [
        ('switchObj', lazy_fixture('sample_switch2_id'), 1),
        ('room', lazy_fixture('sample_port1_room_id'), 2),
        ('room', 4242, 0),
    ]
)
def test_port_get_filter_by_filter(client, filter_name, filter_value, quantity: int, headers, status_code: int):
    r = client.get(
        f"{base_url}/port/?filter[{filter_name}]={filter_value}",
        headers=headers
    )
    assert r.status_code == status_code
    if status_code != 403:
        ports = json.loads(r.data.decode())
        assert len(ports) == quantity

@pytest.mark.parametrize(
    'headers, status_code',
    [
        (TEST_HEADERS, 200),
        (TEST_HEADERS_API_KEY, 200),
        (TEST_HEADERS_SAMPLE, 403),
    ]
)
@pytest.mark.parametrize(
    'term',
    [
        '1.2',
        '0/0/1'
    ]
)
def test_port_get_filter_by_term(client, term: str, headers, status_code: int):
    r = client.get(
        f"{base_url}/port/?terms={term}",
        headers=headers,
    )
    assert r.status_code == status_code
    if status_code != 403:
        ports = json.loads(r.data.decode())
        assert ports
        assert len(ports) == 1


@pytest.mark.parametrize(
    'headers, status_code',
    [
        (TEST_HEADERS, 404),
        (TEST_HEADERS_API_KEY, 404),
        (TEST_HEADERS_SAMPLE, 403),
    ]
)
def test_port_post_create_port_invalid_switch(client, sample_room1, headers, status_code: int):
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
        headers=headers,
    )
    assert r.status_code == status_code


@pytest.mark.parametrize(
    'headers, status_code',
    [
        (TEST_HEADERS, 404),
        (TEST_HEADERS_API_KEY, 404),
        (TEST_HEADERS_SAMPLE, 403),
    ]
)
def test_port_post_create_port_invalid_room(client, sample_switch1, headers, status_code: int):
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
        headers=headers,
    )
    assert r.status_code == status_code


@pytest.mark.parametrize(
    'headers, status_code',
    [
        (TEST_HEADERS, 201),
        (TEST_HEADERS_API_KEY, 201),
        (TEST_HEADERS_SAMPLE, 403),
    ]
)
def test_port_post_create_port(client, sample_switch1, sample_room1, headers, status_code: int):
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
        headers=headers,
    )
    assert r.status_code == status_code


@pytest.mark.parametrize(
    'headers, status_code',
    [
        (TEST_HEADERS, 200),
        (TEST_HEADERS_API_KEY, 200),
        (TEST_HEADERS_SAMPLE, 403),
    ]
)
def test_port_get_existant_port(client, sample_port1, headers, status_code: int):
    r = client.get(
        f"{base_url}/port/{sample_port1.id}",
        headers=headers,
    )
    assert r.status_code == status_code
    if status_code != 403:
        switch = json.loads(r.data.decode())
        assert switch


@pytest.mark.parametrize(
    'headers, status_code',
    [
        (TEST_HEADERS, 404),
        (TEST_HEADERS_API_KEY, 404),
        (TEST_HEADERS_SAMPLE, 404), #TODO: Should be 403
    ]
)
def test_port_get_non_existant_port(client, headers, status_code: int):
    r = client.get(
        f"{base_url}/port/{4242}",
        headers=headers,
    )
    assert r.status_code == status_code

@pytest.fixture
def sample_ports1_id(sample_port1: Port):
    yield sample_port1.id

@pytest.mark.parametrize(
    'headers, status_code_headers',
    [
        (TEST_HEADERS, None),
        (TEST_HEADERS_API_KEY, None),
        (TEST_HEADERS_SAMPLE, 403),
    ]
)
@pytest.mark.parametrize(
    'port_id,key,value,status_code',
    [
        (lazy_fixture('sample_ports1_id'), "switchObj", 999, 404),
        (4242, None, None, 404),
        (lazy_fixture('sample_ports1_id'), "portNumber", "1/2/3", 204),
    ]
)
def test_port_put_update_port(client, sample_switch1: Switch, sample_port1: Port, port_id: int, key: str, value, headers, status_code_headers: Optional[int], status_code: int):
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
        headers=headers,
    )
    assert r.status_code == status_code if status_code_headers is None else status_code_headers
    if r.status_code == 204:
        assert_port_in_db(body)

@pytest.mark.parametrize(
    'headers, status_code_headers',
    [
        (TEST_HEADERS, None),
        (TEST_HEADERS_API_KEY, None),
        #(TEST_HEADERS_SAMPLE, None), # TODO: Should always return 403
    ]
)
@pytest.mark.parametrize(
    'port_id, status_code',
    [
        (lazy_fixture('sample_ports1_id'), 204), 
        (4242, 404)
    ]
)
def test_port_delete_port(client, port_id: int, status_code: int, headers, status_code_headers: Optional[int]):
    r = client.delete(
        f"{base_url}/port/{port_id}",
        headers=headers,
    )
    assert r.status_code == status_code if status_code_headers is None else status_code_headers

    if status_code == 204:
        s = db.session()
        q = s.query(Port)
        q = q.filter(Port.id == port_id)
        assert not s.query(q.exists()).scalar()
