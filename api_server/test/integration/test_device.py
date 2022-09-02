import json

import pytest
from pytest_lazyfixture import lazy_fixture
from adh6.device.storage.device_repository import DeviceType

from adh6.storage import db
from adh6.member.storage.models import Adherent
from adh6.device.storage.models import Device
from test import SAMPLE_CLIENT_ID, TESTING_CLIENT_ID
from test.integration.conftest import sample_member_admin
from .resource import (
    TEST_HEADERS_SAMPLE, base_url as host_url, INVALID_MAC, TEST_HEADERS,
    assert_modification_was_created,
)


base_url = f'{host_url}/device/'


@pytest.fixture
def wireless_device_dict(sample_member):
    '''
    Device that will be inserted/updated when tests are run.
    It is not present in the client by default
    '''
    yield {
        'mac': '01-23-45-67-89-AC',
        'connectionType': 'wireless',
        'member': sample_member.id,
    }


@pytest.fixture
def wired_device_dict(sample_member):
    yield {
        'mac': '01-23-45-67-89-AD',
        'connectionType': 'wired',
        'member': sample_member.id,
    }


@pytest.fixture
def custom_device(sample_member3):
    yield Device(
        id=42,
        mac='96-24-F6-D0-48-A7',
        adherent_id=sample_member3.id,
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
            sample_member3,
            sample_room2,
            sample_vlan,
            sample_room1,
            sample_vlan69,
            sample_room_member_link):
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
            sample_vlan,
            sample_room1,
            sample_vlan69,
            sample_room2,
            sample_room_member_link
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


@pytest.mark.parametrize('member,header,expected', [
    (lazy_fixture('sample_member3'), TEST_HEADERS, 1),
    (lazy_fixture('sample_member'), TEST_HEADERS_SAMPLE, 3),
])
def test_device_filter_wired_by_member(client, header, member, expected):
    r = client.get(
        f'{base_url}?filter[member]={member.id}',
        headers=header
    )
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
        f'{base_url}?filter[terms]={terms}',
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
    for _ in range(LIMIT * 2):
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
def test_device_post(client, sample_room1, device_to_add, sample_member: Adherent):
    """ Can create a valid device """
    r = client.patch(
        f"{host_url}/room/{sample_room1.id}/member/add/",
        data=json.dumps({"id": SAMPLE_CLIENT_ID}),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 204
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
    assert q.one_or_none() is not None
    r = client.get(
        f'{base_url}{int(r.text)}',
        headers=TEST_HEADERS,
        content_type='application/json',
    )
    res = r.json
    assert res["ipv4Address"] == f'{".".join(str(sample_member.subnet).split(".")[:3])}.{int(str(sample_member.subnet).split(".")[3].split("/")[0])+2}' if  device_to_add['connectionType'] == 'wireless' else  res["ipv4Address"] == "192.168.42.2"
    assert res["ipv6Address"] == "fe80:42::2"


def test_device_post_create_multiple_wireless(faker, client, sample_room1, sample_room2, sample_member):
    """
    Can create a valid wired device? Create 20 devices for each users
    """
    r = client.patch(
        f"{host_url}/room/{sample_room2.id}/member/add/",
        data=json.dumps({"id": SAMPLE_CLIENT_ID}),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 204

    r = client.patch(
        f"{host_url}/room/{sample_room1.id}/member/add/",
        data=json.dumps({"id": TESTING_CLIENT_ID}),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 204

    device_number = 12 # 13 should be the maximum but one of the member already have one

    devices = []
    for m in [TESTING_CLIENT_ID, SAMPLE_CLIENT_ID]:
        for _ in range(device_number): 
            d = {
                "mac": faker.mac_address(),
                "member": m,
                'connectionType': 'wireless',
            } 
            devices.append(d)

    for i, d in enumerate(devices):
        r = client.post(
            f'{base_url}',
            data=json.dumps(d),
            content_type='application/json',
            headers=TEST_HEADERS
        )
        assert r.status_code == 201
        r = client.get(
            f'{base_url}{int(r.text)}',
            headers=TEST_HEADERS,
            content_type='application/json',
        )
        res = r.json
        subnet = sample_member.subnet if SAMPLE_CLIENT_ID == d["member"] else sample_member_admin().subnet
        subnet_header = ".".join(subnet.split(".")[:3])
        subnet_start = int(str(subnet).split(".")[3].split("/")[0])+1
        start_number_v6 = [2, 5]
        assert res["ipv4Address"] == f'{subnet_header}.{subnet_start+1+i//device_number+(i%device_number)}'
        assert res["ipv6Address"] == f"fe80:{42 if d['member'] == TESTING_CLIENT_ID else 69}::{format(start_number_v6[i//device_number]+(i%device_number), 'x')}"


def test_device_post_create_multiple_wired(faker, client, sample_room1, sample_room2):
    """
    Can create a valid wired device? Create 20 devices for each users
    """
    r = client.patch(
        f"{host_url}/room/{sample_room2.id}/member/add/",
        data=json.dumps({"id": SAMPLE_CLIENT_ID}),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 204

    r = client.patch(
        f"{host_url}/room/{sample_room1.id}/member/add/",
        data=json.dumps({"id": TESTING_CLIENT_ID}),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 204

    device_number = 15

    devices = []
    for m in [TESTING_CLIENT_ID, SAMPLE_CLIENT_ID]:
        for _ in range(device_number): 
            d = {
                "mac": faker.mac_address(),
                "member": m,
                'connectionType': 'wired',
            } 
            devices.append(d)

    for i, d in enumerate(devices):
        r = client.post(
            f'{base_url}',
            data=json.dumps(d),
            content_type='application/json',
            headers=TEST_HEADERS
        )
        assert r.status_code == 201
        r = client.get(
            f'{base_url}{int(r.text)}',
            headers=TEST_HEADERS,
            content_type='application/json',
        )
        res = r.json
        start_number_v4 = [2, 4]
        start_number_v6 = [2, 5]
        assert res["ipv4Address"] == f"192.168.{42 if d['member'] == TESTING_CLIENT_ID else 69}.{start_number_v4[i//device_number]+(i%device_number)}"
        assert res["ipv6Address"] == f"fe80:{42 if d['member'] == TESTING_CLIENT_ID else 69}::{format(start_number_v6[i//device_number]+(i%device_number), 'x')}"


def test_device_post_create_too_much(faker, client, sample_room1):
    """
    Can create a valid wired device? Create 20 devices for each users
    """
    r = client.patch(
        f"{host_url}/room/{sample_room1.id}/member/add/",
        data=json.dumps({"id": TESTING_CLIENT_ID}),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 204

    max_devices = 20
    devices = []
    for _ in range(20): 
        d = {
            "mac": faker.mac_address(),
            "member": TESTING_CLIENT_ID,
            'connectionType': 'wired',
        } 
        devices.append(d)

    for i, d in enumerate(devices):
        r = client.post(
            f'{base_url}',
            data=json.dumps(d),
            content_type='application/json',
            headers=TEST_HEADERS
        )
        assert r.status_code == 201
        r = client.get(
            f'{base_url}{int(r.text)}',
            headers=TEST_HEADERS,
            content_type='application/json',
        )
        res = r.json
        assert res["ipv4Address"] == f"192.168.42.{2+(i%max_devices)}"
        assert res["ipv6Address"] == f"fe80:42::{format(2+(i%max_devices), 'x')}"

    d = {
        "mac": faker.mac_address(),
        "member": TESTING_CLIENT_ID,
        'connectionType': 'wired',
    } 
    r = client.post(
        f'{base_url}',
        data=json.dumps(d),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert r.status_code == 400


def test_device_post_create_too_much_wireless(faker, client, sample_room1, sample_room2, sample_member):
    """
    Create 13 wireless devices for one user
    """
    r = client.patch(
        f"{host_url}/room/{sample_room1.id}/member/add/",
        data=json.dumps({"id": TESTING_CLIENT_ID}),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 204

    device_number = 13 # 13 should be the maximum /28 -> 16 Ips but we remove broadcast, prefix, gateway

    devices = []
    for _ in range(device_number): 
        d = {
            "mac": faker.mac_address(),
            "member": TESTING_CLIENT_ID,
            'connectionType': 'wireless',
        } 
        devices.append(d)

    for i, d in enumerate(devices):
        r = client.post(
            f'{base_url}',
            data=json.dumps(d),
            content_type='application/json',
            headers=TEST_HEADERS
        )
        assert r.status_code == 201
        r = client.get(
            f'{base_url}{int(r.text)}',
            headers=TEST_HEADERS,
            content_type='application/json',
        )
        res = r.json
        subnet = sample_member_admin().subnet
        subnet_header = ".".join(subnet.split(".")[:3])
        subnet_start = int(str(subnet).split(".")[3].split("/")[0])+1
        assert res["ipv4Address"] == f'{subnet_header}.{subnet_start+1+i//device_number+(i%device_number)}'
        assert res["ipv6Address"] == f"fe80:42::{format(2+(i%device_number), 'x')}"

    d = {
        "mac": faker.mac_address(),
        "member": TESTING_CLIENT_ID,
        'connectionType': 'wireless',
    } 
    r = client.post(
        f'{base_url}',
        data=json.dumps(d),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert r.status_code == 400


@pytest.mark.parametrize(
    'key,value,status_code', 
    [
        ('mac', INVALID_MAC, 400), # Create with invalid mac address
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
    assert json.loads(r.data.decode('utf-8'))


@pytest.mark.parametrize(
    'only', ["mac", "ipv4Address", "ipv6Address", "connectionType", "member"]
)
def test_device_get_only_selected_param(client, wired_device, only):
    r = client.get(
        f'{base_url}{wired_device.id}?only={only}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.data.decode('utf-8'))
    assert len(result.keys()) == 2


def test_device_get_unauthorized(client, custom_device: Device):
    r = client.get(
        f'{base_url}{custom_device.id}',
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


def test_device_get_unauthorized_unknown_device(client):
    r = client.get(
        f'{base_url}{200}',
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


def test_device_delete_unauthorized(client, custom_device: Device):
    r = client.delete(
        f'{base_url}{custom_device.id}',
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


def test_device_delete_unauthorized_unknown_device(client):
    r = client.delete(
        f'{base_url}{200}',
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


@pytest.mark.parametrize(
    'device',
    [
        (lazy_fixture('wired_device')),
        (lazy_fixture('wireless_device')),
    ]
)
def test_device_get_mab(client, device):
    r = client.get(
        f'{base_url}{device.id}/mab/',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    assert not r.json


def test_device_get_mab_unknown_device(client, unknown_device: Device):
    r = client.get(
        f'{base_url}{unknown_device.id}/mab/',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_device_get_mab_unauthorized(client, wired_device: Device):
    r = client.get(
        f'{base_url}{wired_device.id}/mab/',
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


@pytest.mark.parametrize(
    'device',
    [
        (lazy_fixture('wired_device')),
        (lazy_fixture('wireless_device')),
    ]
)
def test_device_post_mab(client, device):
    r = client.post(
        f'{base_url}{device.id}/mab/',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    assert r.json
    r = client.get(
        f'{base_url}{device.id}/mab/',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    assert r.json


def test_device_post_mab_unknown_device(client, unknown_device: Device):
    r = client.post(
        f'{base_url}{unknown_device.id}/mab/',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_device_post_mab_unauthorized(client, wired_device: Device):
    r = client.post(
        f'{base_url}{wired_device.id}/mab/',
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


@pytest.mark.parametrize(
    'device',
    [
        (lazy_fixture('wired_device')),
        (lazy_fixture('wireless_device')),
    ]
)
def test_device_get_owner(client, device, sample_member):
    r = client.get(
        f'{base_url}{device.id}/member/',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    assert r.json == sample_member.id


def test_device_get_owner_unknown_device(client, unknown_device: Device):
    r = client.get(
        f'{base_url}{unknown_device.id}/member/',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_device_get_owner_unauthorized(client, wired_device: Device):
    r = client.get(
        f'{base_url}{wired_device.id}/member/',
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


@pytest.mark.xfail
def test_device_get_vendor(client, wired_device_dict):
    wired_device_dict["mac"] = "00-00-0C-01-23-45"
    r = client.post(
        f'{base_url}',
        data=json.dumps(wired_device_dict),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert r.status_code == 201
    result = r.json
    r = client.get(
        f'{base_url}{result}/vendor/',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    assert r.json == "Cisco Systems, Inc\n"


def test_device_get_vendor_unknown_device(client, unknown_device: Device):
    r = client.get(
        f'{base_url}{unknown_device.id}/vendor/',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_device_get_vendor_unauthorized(client, custom_device: Device):
    r = client.get(
        f'{base_url}{custom_device.id}/vendor/',
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


def test_device_get_vendor_unauthorized_unknown_device(client):
    r = client.get(
        f'{base_url}{200}/vendor/',
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403
