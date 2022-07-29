import json

import pytest
from pytest_lazyfixture import lazy_fixture
from adh6.device.storage.device_repository import DeviceType

from adh6.storage.sql.models import Adherent, db, Device
from .resource import (
    TEST_HEADERS_SAMPLE, base_url as host_url, INVALID_MAC, INVALID_IP, INVALID_IPv6, TEST_HEADERS,
    assert_modification_was_created,
)
from test import (
    SAMPLE_CLIENT_ID, TESTING_CLIENT_ID
)


base_url = f'{host_url}/device/'


@pytest.fixture
def custom_device(sample_member):
    yield Device(
        id=42,
        mac='96-24-F6-D0-48-A7',
        adherent_id=sample_member.id,
        type=DeviceType.wired.value,
        ip='157.159.1.1',
        ipv6='::1',
    )

@pytest.fixture
def unknown_device(faker, sample_member):
    yield Device(
        id=faker.random_digit_not_null(),
        mac=faker.mac_address(),
        adherent_id=sample_member.id,
        type=DeviceType.wired.value,
        ip=faker.ipv4_public(),
        ipv6=faker.ipv6(),
    )

@pytest.fixture
def device_with_invalid_member(faker, sample_device: Device):
    yield Device(
        id=sample_device.id,
        mac=sample_device.mac,
        adherent_id=faker.random_digit_not_null(),
        type=DeviceType.wired.value,
        ip=sample_device.ip,
        ipv6=sample_device.ipv6,
    )


@pytest.fixture
def client(custom_device,
            wired_device,
            wired_device2,
            wireless_device,
            sample_member,
            sample_member3):
    from .context import app
    from .conftest import prep_db, close_db
    if app.app is None:
        return
    with app.app.test_client() as c:
        prep_db(
            custom_device,
            wired_device,
            wired_device2,
            wireless_device,
            sample_member,
            sample_member3,
        )
        yield c
        close_db()

def test_device_filter_all_devices(client):
    r = client.get(
        f'{base_url}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 4

@pytest.mark.parametrize(
    'sample_only', 
    [
        ("id"),
        ("mac"),
        ("ipv4Address"),
        ("ipv6Address"),
        ("connectionType"),
        ("member"),
        ("ipv4Address,ipv6Address"),
    ])
def test_device_filter_with_only(client, sample_only: str):
    r = client.get(
        f'{base_url}?only={sample_only}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 4
    assert len(set(sample_only.split(",") + ["__typename", "id"])) == len(set(response[0].keys()))

def test_device_filter_with_unknown_only(client):
    sample_only = "azerty"
    r = client.get(
        f'{base_url}?only={sample_only}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400

@pytest.mark.parametrize('member,header,expected', [
    (lazy_fixture('sample_member3'), TEST_HEADERS, 0),
    (lazy_fixture('sample_member'), TEST_HEADERS_SAMPLE, 4),
])
def test_device_filter_wired_by_member(client, header, member, expected):
    r = client.get(
        f'{base_url}?filter[member]={member.id}',
        headers=header
    )
    print(r.text)
    assert r.status_code == 200
    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == expected

@pytest.mark.parametrize('terms,expected', [
    ('96-24-F6-D0-48-A7', 1),  # Should find sample wired device
    ('96-', 1),
    ('f6-d0', 1),
    ('157.159', 1),
    ('80-65-F3-FC-44-A9', 0),  # Should find nothing
    ('::1', 1),
    ('-', 4),  # Should find everything
    ('00-', 0),  # Should find nothing
])
def test_device_filter_by_terms(client, terms, expected):
    r = client.get(
        f'{base_url}?terms={terms}',
        headers=TEST_HEADERS
    )
    assert r.status_code == 200
    
    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == expected


def test_device_filter_invalid_limit(client):
    r = client.get(
        f'{base_url}?limit={-1}',
        headers=TEST_HEADERS
    )
    assert r.status_code == 400


def test_device_filter_hit_limit(client, sample_member: Adherent):
    s = db.session()
    LIMIT = 10

    # Create a lot of devices
    for i in range(LIMIT * 2):
        suffix = "{0:04X}"
        dev = Device(
            adherent_id=sample_member.id,
            mac='00-00-00-00-' + suffix[:2] + "-" + suffix[2:],
            type=DeviceType.wired.value,
            ip="127.0.0.1",
            ipv6="::1",
        )
        s.add(dev)
    s.commit()

    r = client.get(
        f'{base_url}?limit={LIMIT}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == LIMIT


@pytest.mark.parametrize(
    'device',
    [lazy_fixture('wireless_device'), lazy_fixture('wired_device')]
)
def test_device_filter_by_id(client, device: Device):
    r = client.get(
        f'{base_url}?filter[id]={device.id}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 1


@pytest.mark.parametrize(
    'device',
    [lazy_fixture('wireless_device'), lazy_fixture('wired_device')]
)
def test_device_filter_by_connection_type(client, device: Device):
    r = client.get(
        f'{base_url}?filter[connectionType]={"wireless"}' if device.type == DeviceType.wireless.value else f'{base_url}?filter[connectionType]={"wired"}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 1 if device.type == DeviceType.wireless.value else 3


def test_device_filter_unauthorized(client):
    r = client.get(
        f'{base_url}',
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403

@pytest.mark.parametrize(
    'device_to_add',
    [lazy_fixture('wireless_device_dict'), lazy_fixture('wired_device_dict')]
)
def test_device_post(client, device_to_add):
    """ Can create a valid device """
    r = client.post(
        f'{base_url}',
        data=json.dumps(device_to_add),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert r.status_code == 201
    assert_modification_was_created(db.session())

    s = db.session()
    q = s.query(Device)
    q = q.filter(Device.type == (DeviceType.wireless.value if device_to_add['connectionType'] == 'wireless' else DeviceType.wired.value))
    q = q.filter(Device.mac == device_to_add['mac'])
    _ = q.one()


def test_device_post_create_wired_without_ip(client, wired_device_dict):
    """
    Can create a valid wired device? Create two devices and check the IP
    """

    del wired_device_dict['ipv4Address']
    del wired_device_dict['ipv6Address']
    r = client.post(
        f'{base_url}',
        data=json.dumps(wired_device_dict),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert r.status_code == 201
    assert_modification_was_created(db.session())

    wired_device_dict["mac"] = "AB-CD-EF-01-23-45"
    r = client.post(
        f'{base_url}',
        data=json.dumps(wired_device_dict),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert r.status_code == 201
    assert_modification_was_created(db.session())


@pytest.mark.parametrize(
    'key,value,status_code', 
    [
        ('mac', INVALID_MAC, 400), # Create with invalid mac address
        ('ipv6Address', INVALID_IPv6, 400), # Create with invalid ipv6 address
        ('ipv4Address', INVALID_IP, 400), # Create with invalid ipv4 address
        ('member', 4242, 404), # Create with invalid member
    ]
)
def test_device_post_create_invalid(client, key, value, wired_device_dict, status_code):
    wired_device_dict[key] = value
    r = client.post(
        f'{base_url}',
        data=json.dumps(wired_device_dict),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == status_code


def test_device_post_create_unauthorized(client, wired_device_dict):
    wired_device_dict["member"] = 4242
    r = client.post(
        f'{base_url}',
        data=json.dumps(wired_device_dict),
        content_type='application/json',
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


@pytest.mark.parametrize(
    'device_to_patch',
    [lazy_fixture('wireless_device'), lazy_fixture('wired_device')]
)
@pytest.mark.parametrize(
    'value',
    [lazy_fixture('wireless_device_dict'), lazy_fixture('wired_device_dict')]
)
def test_device_patch(client, device_to_patch: Device, value):
    r = client.patch(
        f'{base_url}{device_to_patch.id}',
        data=json.dumps(value),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert r.status_code == 204
    assert_modification_was_created(db.session())


def test_device_patch_unauthorized_not_owner(client, wired_device: Device, wired_device_dict):
    wired_device_dict["member"] = TESTING_CLIENT_ID
    r = client.patch(
        f'{base_url}{wired_device.id}',
        data=json.dumps(wired_device_dict),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    wired_device_dict["member"] = SAMPLE_CLIENT_ID
    r = client.patch(
        f'{base_url}{wired_device.id}',
        data=json.dumps(wired_device_dict),
        content_type='application/json',
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


def test_device_patch_unauthorized(client, wired_device: Device, wired_device_dict):
    wired_device_dict["member"] = 4242
    r = client.patch(
        f'{base_url}{wired_device.id}',
        data=json.dumps(wired_device_dict),
        content_type='application/json',
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


@pytest.mark.parametrize(
    'device, status_code',
    [
        (lazy_fixture('wired_device'), 200),
        (lazy_fixture('wireless_device'), 200),
        (lazy_fixture('unknown_device'), 404),
    ]
)
def test_device_get_valid(client, device, status_code):
    r = client.get(
        f'{base_url}{device.id}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == status_code
    if status_code != 403:
        assert json.loads(r.data.decode('utf-8'))


def test_device_get_unauthorized(client, wired_device: Device, wired_device_dict):
    wired_device_dict["member"] = TESTING_CLIENT_ID
    r = client.patch(
        f'{base_url}{wired_device.id}',
        data=json.dumps(wired_device_dict),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    r = client.get(
        f'{base_url}{wired_device.id}',
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


@pytest.mark.parametrize(
    'device, status_code',
    [
        (lazy_fixture('wired_device'), 204),
        (lazy_fixture('wireless_device'), 204),
        (lazy_fixture('unknown_device'), 404),
    ]
)
def test_device_delete(client, device: Device, status_code: int):
    r = client.delete(
        f'{base_url}{device.id}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == status_code
    if status_code == 204:
        assert_modification_was_created(db.session())

        s = db.session()
        q = s.query(Device)
        q = q.filter(Device.type == "wired")
        q = q.filter(Device.mac == device.mac)
        assert not s.query(q.exists()).scalar(), "Object not actually deleted"


def test_device_delete_unauthorized(client, wired_device: Device, wired_device_dict):
    wired_device_dict["member"] = TESTING_CLIENT_ID
    r = client.patch(
        f'{base_url}{wired_device.id}',
        data=json.dumps(wired_device_dict),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    r = client.delete(
        f'{base_url}{wired_device.id}',
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403
