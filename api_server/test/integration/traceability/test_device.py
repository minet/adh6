import logging
import pytest

from src.interface_adapter.http_api.auth import TESTING_CLIENT
from test.integration.resource import logs_contains
from test.integration.test_device import test_device_post_create_wired, test_device_post_create_wireless, \
    test_device_patch_update_wired, test_device_patch_update_wireless, test_device_delete_wired, test_device_delete_wireless


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

def test_device_log_create_wired(client, caplog, wired_device_dict):
    with caplog.at_level(logging.INFO):
        test_device_post_create_wired(client, wired_device_dict)

    assert logs_contains(caplog,
                         'device_manager_update_or_create',
                         user=TESTING_CLIENT)


def test_device_log_create_wireless(client, caplog, wireless_device_dict):
    with caplog.at_level(logging.INFO):
        test_device_post_create_wireless(client, wireless_device_dict)

    assert logs_contains(caplog,
                         'device_manager_update_or_create',
                         user=TESTING_CLIENT)


def test_device_log_update_wired(client, caplog, wired_device,
                                 wired_device_dict):
    with caplog.at_level(logging.INFO):
        test_device_patch_update_wired(client, wired_device,
                                     wired_device_dict)

    assert logs_contains(caplog,
                         'device_manager_partially_update',
                         user=TESTING_CLIENT,
                         device_id=wired_device.id)


def test_device_log_update_wireless(client, caplog, wireless_device,
                                    wireless_device_dict):
    with caplog.at_level(logging.INFO):
        test_device_patch_update_wireless(client, wireless_device,
                                        wireless_device_dict)

    assert logs_contains(caplog,
                         'device_manager_partially_update',
                         user=TESTING_CLIENT,
                         device_id=wireless_device.id)


def test_device_log_delete_wired(client, caplog, wired_device,
                                 wired_device_dict):
    with caplog.at_level(logging.INFO):
        test_device_delete_wired(client, wired_device)

    assert logs_contains(caplog,
                         'device_manager_delete',
                         user=TESTING_CLIENT,
                         device_id=wired_device.id)


def test_device_log_delete_wireless(client, caplog, wireless_device,
                                    wireless_device_dict):
    with caplog.at_level(logging.INFO):
        test_device_delete_wireless(client, wireless_device)

    assert logs_contains(caplog,
                         'device_manager_delete',
                         user=TESTING_CLIENT,
                         device_id=wireless_device.id)
