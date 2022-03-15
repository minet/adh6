import json

import pytest
from pytest_lazyfixture import lazy_fixture

from src.interface_adapter.sql.device_repository import DeviceType
from src.interface_adapter.sql.model.models import Adherent, db, Device
from .resource import (
    TEST_HEADERS_SAMPLE, TEST_HEADERS_SAMPLE2, base_url, INVALID_MAC, INVALID_IP, INVALID_IPv6, TEST_HEADERS,
    assert_modification_was_created)


@pytest.fixture
def custom_device(sample_member):
    yield Device(
        id=42,
        mac='96-24-F6-D0-48-A7',
        adherent=sample_member,
        type=DeviceType.wired.value,
        ip='157.159.1.1',
        ipv6='::1',
    )

@pytest.fixture
def unknown_device(faker, sample_member):
    yield Device(
        id=faker.random_digit_not_null(),
        mac=faker.mac_address(),
        adherent=sample_member,
        type=DeviceType.wired.value,
        ip=faker.ipv4_public(),
        ipv6=faker.ipv6(),
    )

@pytest.fixture
def device_with_invalid_member(faker, sample_device: Device):
    yield Device(
        id=sample_device,
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
            sample_member3,
            sample_member2):
    from .context import app
    from .conftest import prep_db, close_db
    with app.app.test_client() as c:
        prep_db(
            custom_device,
            wired_device,
            wired_device2,
            wireless_device,
            sample_member3,
        )
        yield c
        close_db()


def test_device_filter_all_devices(client):
    r = client.get(
        f'{base_url}/device/',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 4

@pytest.mark.parametrize('member,header,expected, code', [
    (lazy_fixture('sample_member'), TEST_HEADERS, 4, 200),
    (lazy_fixture('sample_member3'), TEST_HEADERS, 0, 200),
    (lazy_fixture('sample_member'), TEST_HEADERS_SAMPLE, 4, 200),
    (lazy_fixture('sample_member3'), TEST_HEADERS_SAMPLE, 0, 403),
])
def test_device_filter_wired_by_member(client, header, member, expected, code):
    r = client.get(
        f'{base_url}/device/?filter[member]={member.id}',
        headers=header
    )
    assert r.status_code == code
    if code == 200:
        response = json.loads(r.data.decode('utf-8'))
        assert len(response) == expected

@pytest.mark.parametrize(
    'headers, status_code',
    [
        (TEST_HEADERS, 200),
        (TEST_HEADERS_SAMPLE, 403),
    ]
)
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
def test_device_filter_by_terms(client, terms, expected, headers, status_code):
    r = client.get(
        f'{base_url}/device/?terms={terms}',
        headers=headers
    )
    assert r.status_code == status_code
    
    if status_code == 200:
        response = json.loads(r.data.decode('utf-8'))
        assert len(response) == expected


@pytest.mark.parametrize(
    'headers, status_code',
    [
        (TEST_HEADERS, 400),
        (TEST_HEADERS_SAMPLE, 403),
    ]
)
def test_device_filter_invalid_limit(client, headers, status_code: int):
    r = client.get(
        f'{base_url}/device/?limit={-1}',
        headers=headers
    )
    assert r.status_code == status_code


@pytest.mark.parametrize(
    'headers, status_code',
    [
        (TEST_HEADERS, 200),
        (TEST_HEADERS_SAMPLE, 403),
    ]
)
def test_device_filter_hit_limit(client, sample_member: Adherent, headers, status_code: int):
    s = db.session()
    LIMIT = 10

    # Create a lot of devices
    for i in range(LIMIT * 2):
        suffix = "{0:04X}".format(i)
        dev = Device(
            adherent=sample_member,
            mac='00-00-00-00-' + suffix[:2] + "-" + suffix[2:],
            type=DeviceType.wired.value,
            ip="127.0.0.1",
            ipv6="::1",
        )
        s.add(dev)
    s.commit()

    r = client.get(
        f'{base_url}/device/?limit={LIMIT}',
        headers=headers,
    )
    assert r.status_code == status_code
    if status_code == 200:
        response = json.loads(r.data.decode('utf-8'))
        assert len(response) == LIMIT

@pytest.mark.parametrize(
    'headers, status_code',
    [
        (TEST_HEADERS, 201),
        (TEST_HEADERS_SAMPLE, 201),
        (TEST_HEADERS_SAMPLE2, 403),
    ]
)
@pytest.mark.parametrize(
    'device_to_add',
    [lazy_fixture('wireless_device_dict'), lazy_fixture('wired_device_dict')]
)
def test_device_post(client, device_to_add, headers, status_code):
    """ Can create a valid device """
    r = client.post(
        f'{base_url}/device/',
        data=json.dumps(device_to_add),
        content_type='application/json',
        headers=headers
    )
    assert r.status_code == status_code

    if status_code != 403:
        assert_modification_was_created(db.session())

        s = db.session()
        q = s.query(Device)
        q = q.filter(Device.type == (DeviceType.wireless.value if device_to_add['connectionType'] == 'wireless' else DeviceType.wired.value))
        q = q.filter(Device.mac == device_to_add['mac'])
        _ = q.one()


@pytest.mark.parametrize(
    'headers, status_code',
    [
        (TEST_HEADERS, 201),
        (TEST_HEADERS_SAMPLE, 201),
        (TEST_HEADERS_SAMPLE2, 403),
    ]
)
def test_device_post_create_wired_without_ip(client, wired_device_dict, headers, status_code):
    """
    Can create a valid wired device? Create two devices and check the IP
    """

    del wired_device_dict['ipv4Address']
    del wired_device_dict['ipv6Address']
    r = client.post(
        f'{base_url}/device/',
        data=json.dumps(wired_device_dict),
        content_type='application/json',
        headers=headers
    )
    assert r.status_code == status_code
    if status_code != 403:
        assert_modification_was_created(db.session())

    wired_device_dict["mac"] = "AB-CD-EF-01-23-45"
    r = client.post(
        f'{base_url}/device/',
        data=json.dumps(wired_device_dict),
        content_type='application/json',
        headers=headers
    )
    assert r.status_code == status_code
    
    if status_code != 403:
        assert_modification_was_created(db.session())

        s = db.session()
        q = s.query(Device)
        q = q.filter(Device.type == DeviceType.wired.value)
        q = q.filter(Device.mac == wired_device_dict["mac"])
        dev = q.one()
        assert dev.ip == '192.168.42.12'
        assert dev.ipv6 == 'fe80::c'


@pytest.mark.parametrize(
    'headers',
    [
        (TEST_HEADERS),
        (TEST_HEADERS_SAMPLE),
        (TEST_HEADERS_SAMPLE2),
    ]
)
@pytest.mark.parametrize(
    'key,value,status_code', 
    [
        ('mac', INVALID_MAC, 400), # Create with invalid mac address
        ('ipv6Address', INVALID_IPv6, 400), # Create with invalid ipv6 address
        ('ipv4Address', INVALID_IP, 400), # Create with invalid ipv4 address
        ('member', 4242, 403), # Create with invalid member
    ]
)
def test_device_post_create_invalid(client, key, value, status_code, wired_device_dict, headers):
    wired_device_dict[key] = value
    r = client.post(
        f'{base_url}/device/',
        data=json.dumps(wired_device_dict),
        content_type='application/json',
        headers=headers,
    )
    if headers == TEST_HEADERS and key == 'member':
        assert r.status_code == 404
    else:
        assert r.status_code == status_code

@pytest.mark.parametrize(
    'headers, status_code',
    [
        (TEST_HEADERS, 204),
        (TEST_HEADERS_SAMPLE, 204),
        (TEST_HEADERS_SAMPLE2, 403),
    ]
)
@pytest.mark.parametrize(
    'device_to_patch',
    [lazy_fixture('wireless_device'), lazy_fixture('wired_device')]
)
@pytest.mark.parametrize(
    'value',
    [lazy_fixture('wireless_device_dict'), lazy_fixture('wired_device_dict')]
)
def test_device_patch(client, device_to_patch: Device, value, headers, status_code):
    r = client.patch(
        f'{base_url}/device/{device_to_patch.id}',
        data=json.dumps(value),
        content_type='application/json',
        headers=headers
    )
    assert r.status_code == status_code
    if status_code != 403:
        assert_modification_was_created(db.session())

@pytest.mark.parametrize(
    'headers',
    [
        (TEST_HEADERS),
        (TEST_HEADERS_SAMPLE),
        (TEST_HEADERS_SAMPLE2),
    ]
)
@pytest.mark.parametrize(
    'device, status_code',
    [
        (lazy_fixture('wired_device'), 200),
        (lazy_fixture('wireless_device'), 200),
        (lazy_fixture('unknown_device'), 404),
    ]
)
def test_device_get_valid(client, device, status_code, headers):
    if headers == TEST_HEADERS_SAMPLE2 and db.session.query(Device).filter(Device.id == device.id).one_or_none() is not None:
        status_code = 403
    r = client.get(
        f'{base_url}/device/{device.id}',
        headers=headers,
    )
    assert r.status_code == status_code
    if status_code != 403:
        assert json.loads(r.data.decode('utf-8'))

@pytest.mark.parametrize(
    'header',
    [
        (TEST_HEADERS),
        (TEST_HEADERS_SAMPLE)
    ]
)
@pytest.mark.parametrize(
    'device, status_code',
    [
        (lazy_fixture('wired_device'), 204),
        (lazy_fixture('wireless_device'), 204),
        (lazy_fixture('unknown_device'), 404),
    ]
)
def test_device_delete(client, device: Device, header, status_code: int):
    r = client.delete(
        f'{base_url}/device/{device.id}',
        headers=header,
    )
    assert r.status_code == status_code
    if status_code == 204:
        assert_modification_was_created(db.session())

        s = db.session()
        q = s.query(Device)
        q = q.filter(Device.type == "wired")
        q = q.filter(Device.mac == device.mac)
        assert not s.query(q.exists()).scalar(), "Object not actually deleted"
