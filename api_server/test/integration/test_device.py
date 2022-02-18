import json

import pytest
from pytest_lazyfixture import lazy_fixture

from src.interface_adapter.sql.device_repository import DeviceType
from src.interface_adapter.sql.model.models import db
from src.interface_adapter.sql.model.models import Device
from .resource import (
    base_url, INVALID_MAC, INVALID_IP, INVALID_IPv6, TEST_HEADERS,
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


def prep_db(session,
            custom_device,
            wired_device,
            wired_device2,
            wireless_device,
            sample_member3):
    session.add_all([
        custom_device,
        wired_device,
        wired_device2,
        wireless_device,
        sample_member3,
    ])
    session.commit()


@pytest.fixture
def api_client(wired_device,
               custom_device,
               wired_device2,
               wireless_device,
               sample_member3):
    from .context import app
    with app.app.test_client() as c:
        db.create_all()
        prep_db(db.session(),
                custom_device,
                wired_device,
                wired_device2,
                wireless_device,
                sample_member3)
        yield c
        db.session.remove()
        db.drop_all()


def test_device_filter_all_devices(api_client):
    r = api_client.get(
        '{}/device/'.format(base_url),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 4

@pytest.mark.parametrize('member,expected', [
    (lazy_fixture('sample_member'), 3),
    (lazy_fixture('sample_member2'), 1),
    (lazy_fixture('sample_member3'), 0)
])
def test_device_filter_wired_by_member(api_client, member, expected):
    id = member.id
    print(member)
    print("")
    r = api_client.get(
        '{}/device/?filter[member]={}'.format(
            base_url,
            member.id
        ),
        headers=TEST_HEADERS
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
def test_device_filter_by_terms(
        api_client, wired_device, terms, expected):
    r = api_client.get(
        '{}/device/?terms={}'.format(
            base_url,
            terms,
        ),
        headers=TEST_HEADERS
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == expected


def test_device_filter_invalid_limit(api_client):
    r = api_client.get(
        '{}/device/?limit={}'.format(base_url, -1),
        headers=TEST_HEADERS
    )
    assert r.status_code == 400


def test_device_filter_hit_limit(api_client, sample_member):
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

    r = api_client.get(
        '{}/device/?limit={}'.format(base_url, LIMIT),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == LIMIT


def test_device_post_create_wireless(api_client, wireless_device_dict):
    """ Can create a valid wireless device ? """
    addr = '{}/device/'.format(base_url)
    r = api_client.post(addr,
                       data=json.dumps(wireless_device_dict),
                       content_type='application/json',
                       headers=TEST_HEADERS)
    assert r.status_code == 201
    assert_modification_was_created(db.session())


def test_device_post_create_wired_without_ip(api_client, wired_device_dict):
    """
    Can create a valid wired device? Create two devices and check the IP
    """

    del wired_device_dict['ipv4Address']
    del wired_device_dict['ipv6Address']
    r = api_client.post('{}/device/'.format(base_url),
                       data=json.dumps(wired_device_dict),
                       content_type='application/json',
                       headers=TEST_HEADERS)
    assert r.status_code == 201
    assert_modification_was_created(db.session())

    wired_device_dict["mac"] = "AB-CD-EF-01-23-45"
    r = api_client.post('{}/device/'.format(base_url),
                       data=json.dumps(wired_device_dict),
                       content_type='application/json',
                       headers=TEST_HEADERS)
    assert r.status_code == 201
    assert_modification_was_created(db.session())

    s = db.session()
    q = s.query(Device)
    q = q.filter(Device.type == DeviceType.wired.value)
    q = q.filter(Device.mac == wired_device_dict["mac"])
    dev = q.one()
    assert dev.ip == '192.168.42.12'
    assert dev.ipv6 == 'fe80::c'


def test_device_post_create_wired(api_client, wired_device_dict):
    ''' Can create a valid wired device ? '''
    r = api_client.post('{}/device/'.format(base_url),
                       data=json.dumps(wired_device_dict),
                       content_type='application/json',
                       headers=TEST_HEADERS)
    assert r.status_code == 201
    assert_modification_was_created(db.session())

    s = db.session()
    q = s.query(Device)
    q = q.filter(Device.type == DeviceType.wired.value)
    q = q.filter(Device.mac == wired_device_dict["mac"])
    dev = q.one()
    assert dev.ip == "127.0.0.1"


@pytest.mark.parametrize('test_mac', [(INVALID_MAC,)])
def test_device_post_create_invalid_mac_address(api_client,
                                               test_mac,
                                               wired_device_dict):
    ''' Create with invalid mac address '''
    wired_device_dict['mac'] = test_mac
    r = api_client.post(
        '{}/device/'.format(base_url),
        data=json.dumps(wired_device_dict),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400 or r.status_code == 405


@pytest.mark.parametrize('test_ip', [(INVALID_IPv6,)])
def test_device_post_create_invalid_ipv6(api_client, test_ip,
                                        wired_device_dict):
    ''' Create with invalid ip address '''
    wired_device_dict['ipv6Address'] = test_ip
    r = api_client.post(
        '{}/device/'.format(base_url),
        data=json.dumps(wired_device_dict),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


@pytest.mark.parametrize('test_ip', [(INVALID_IP,)])
def test_device_post_create_invalid_ipv4(api_client, test_ip,
                                        wired_device_dict):
    ''' Create with invalid ip address '''
    wired_device_dict['ipv4Address'] = test_ip
    r = api_client.post(
        '{}/device/'.format(base_url),
        data=json.dumps(wired_device_dict),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_device_post_create_invalid_member(api_client, wired_device_dict):
    ''' Create with invalid mac address '''
    wired_device_dict['member'] = 4242
    r = api_client.post(
        '{}/device/'.format(base_url),
        data=json.dumps(wired_device_dict),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_device_patch_update_wireless(api_client, wireless_device,
                                    wireless_device_dict):
    ''' Can update a valid wireless device ? '''
    r = api_client.patch(
        '{}/device/{}'.format(base_url, wireless_device.id),
        data=json.dumps(wireless_device_dict),
        content_type='application/json',
        headers=TEST_HEADERS)
    assert r.status_code == 204
    assert_modification_was_created(db.session())


def test_device_patch_update_wired(api_client, wired_device, wired_device_dict):
    ''' Can update a valid wired device ? '''
    r = api_client.patch(
        '{}/device/{}'.format(base_url, wired_device.id),
        data=json.dumps(wired_device_dict),
        content_type='application/json',
        headers=TEST_HEADERS)
    assert r.status_code == 204
    assert_modification_was_created(db.session())


def test_device_patch_update_wired_to_wireless(api_client, wired_device,
                                             wireless_device_dict):
    ''' Can update a valid wired device and cast it into a wireless d ? '''
    r = api_client.patch(
        '{}/device/{}'.format(base_url, wired_device.id),
        data=json.dumps(wireless_device_dict),
        content_type='application/json',
        headers=TEST_HEADERS)
    assert r.status_code == 204
    assert_modification_was_created(db.session())


def test_device_patch_update_wireless_to_wired(api_client,
                                             wireless_device,
                                             wired_device_dict):
    ''' Can update a valid wireless device and cast it into a wired d ? '''
    r = api_client.patch(
        '{}/device/{}'.format(base_url, wireless_device.id),
        data=json.dumps(wired_device_dict),
        content_type='application/json',
        headers=TEST_HEADERS)
    assert r.status_code == 204
    assert_modification_was_created(db.session())


def test_device_get_unknown_id(api_client):
    id = 1234
    r = api_client.get(
        '{}/device/{}'.format(base_url, id),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_device_get_valid_wired(api_client, wired_device):
    r = api_client.get(
        '{}/device/{}'.format(base_url, wired_device.id),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    assert json.loads(r.data.decode('utf-8'))


def test_device_get_valid_wireless(api_client, wireless_device):
    r = api_client.get(
        '{}/device/{}'.format(base_url, wireless_device.id),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    assert json.loads(r.data.decode('utf-8'))


def test_device_delete_wired(api_client, wired_device):
    r = api_client.delete(
        '{}/device/{}'.format(base_url, wired_device.id),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 204
    assert_modification_was_created(db.session())

    s = db.session()
    q = s.query(Device)
    q = q.filter(Device.type == "wired")
    q = q.filter(Device.mac == wired_device.mac)
    assert not s.query(q.exists()).scalar(), "Object not actually deleted"


def test_device_delete_wireless(api_client, wireless_device):
    r = api_client.delete(
        '{}/device/{}'.format(base_url, wireless_device.id),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 204
    assert_modification_was_created(db.session())

    s = db.session()
    q = s.query(Device)
    q = q.filter(Device.type == "wireless")
    q = q.filter(Device.mac == wireless_device.mac)
    assert not s.query(q.exists()).scalar(), "Object not actually deleted"


def test_device_delete_unexistant(api_client):
    id = 1234
    r = api_client.delete(
        '{}/device/{}'.format(base_url, id),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404
