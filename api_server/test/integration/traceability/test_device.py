import logging
import pytest
from pytest_lazyfixture import lazy_fixture

from test.auth import TESTING_CLIENT
from src.interface_adapter.sql.model.models import Device
from test.integration.resource import TEST_HEADERS, logs_contains


@pytest.fixture
def client(wired_device,
            wireless_device,
            sample_member3):
    from ..context import app
    from ..conftest import prep_db, close_db
    with app.app.test_client() as c:
        prep_db(
            wired_device,
            wireless_device,
            sample_member3
        )
        yield c
        close_db()


@pytest.mark.parametrize(
    'device_dict',
    [lazy_fixture('wired_device_dict'), lazy_fixture('wireless_device_dict')]
)
def test_device_log_create_wireless(client, caplog, device_dict):
    with caplog.at_level(logging.INFO):
        from test.integration.test_device import test_device_post
        test_device_post(client, device_dict, TEST_HEADERS, 201)

    assert logs_contains(caplog,
                         'device_manager_update_or_create',
                         user=TESTING_CLIENT)


@pytest.mark.parametrize(
    'device, device_dict',
    [
        (lazy_fixture('wired_device'), lazy_fixture('wired_device_dict')), 
        (lazy_fixture('wireless_device'), lazy_fixture('wireless_device_dict'))
    ]
)
def test_device_log_update(client, caplog, device: Device, device_dict):
    with caplog.at_level(logging.INFO):
        from test.integration.test_device import test_device_patch
        test_device_patch(client, device, device_dict, TEST_HEADERS, 204)

    assert logs_contains(caplog,
                         'device_manager_partially_update',
                         user=TESTING_CLIENT,
                         device_id=device.id)


@pytest.mark.parametrize(
    'device',
    [lazy_fixture('wired_device'), lazy_fixture('wireless_device')]
)
def test_device_log_delete(client, caplog, device: Device):
    with caplog.at_level(logging.INFO):
        from test.integration.test_device import test_device_delete
        test_device_delete(client, device, TEST_HEADERS, 204)

    assert logs_contains(caplog,
                         'device_manager_delete',
                         device_id=device.id)
