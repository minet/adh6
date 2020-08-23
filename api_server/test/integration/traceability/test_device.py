import logging
import pytest

from config.TEST_CONFIGURATION import DATABASE
from src.interface_adapter.http_api.auth import TESTING_CLIENT
from src.interface_adapter.sql.model.database import Database as db
from test.integration.resource import logs_contains
from test.integration.test_device import test_device_post_create_wired, test_device_post_create_wireless, \
    test_device_patch_update_wired, test_device_patch_update_wireless, test_device_delete_wired, test_device_delete_wireless


def prep_db(session,
            wired_device,
            wireless_device,
            sample_member3):
    session.add_all([
        wired_device,
        wireless_device,
        sample_member3,
    ])
    session.commit()


@pytest.fixture
def api_client(wired_device,
               wireless_device,
               sample_member3):
    from ..context import app
    with app.app.test_client() as c:
        db.init_db(DATABASE, testing=True)
        prep_db(db.get_db().get_session(),
                wired_device,
                wireless_device,
                sample_member3)
        yield c


def test_device_log_create_wired(api_client, caplog, wired_device_dict):
    with caplog.at_level(logging.INFO):
        test_device_post_create_wired(api_client, wired_device_dict)

    assert logs_contains(caplog,
                         'device_manager_update_or_create',
                         admin=TESTING_CLIENT)


def test_device_log_create_wireless(api_client, caplog, wireless_device_dict):
    with caplog.at_level(logging.INFO):
        test_device_post_create_wireless(api_client, wireless_device_dict)

    assert logs_contains(caplog,
                         'device_manager_update_or_create',
                         admin=TESTING_CLIENT)


def test_device_log_update_wired(api_client, caplog, wired_device,
                                 wired_device_dict):
    with caplog.at_level(logging.INFO):
        test_device_patch_update_wired(api_client, wired_device,
                                     wired_device_dict)

    assert logs_contains(caplog,
                         'device_manager_partially_update',
                         admin=TESTING_CLIENT,
                         device_id=wired_device.id)


def test_device_log_update_wireless(api_client, caplog, wireless_device,
                                    wireless_device_dict):
    with caplog.at_level(logging.INFO):
        test_device_patch_update_wireless(api_client, wireless_device,
                                        wireless_device_dict)

    assert logs_contains(caplog,
                         'device_manager_partially_update',
                         admin=TESTING_CLIENT,
                         device_id=wireless_device.id)


def test_device_log_delete_wired(api_client, caplog, wired_device,
                                 wired_device_dict):
    with caplog.at_level(logging.INFO):
        test_device_delete_wired(api_client, wired_device)

    assert logs_contains(caplog,
                         'device_manager_delete',
                         admin=TESTING_CLIENT,
                         device_id=wired_device.id)


def test_device_log_delete_wireless(api_client, caplog, wireless_device,
                                    wireless_device_dict):
    with caplog.at_level(logging.INFO):
        test_device_delete_wireless(api_client, wireless_device)

    assert logs_contains(caplog,
                         'device_manager_delete',
                         admin=TESTING_CLIENT,
                         device_id=wireless_device.id)
