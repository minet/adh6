import logging
import pytest

from src.interface_adapter.http_api.auth import TESTING_CLIENT
from src.interface_adapter.sql.model.models import  db
from test.integration.resource import logs_contains
from test.integration.test_port import test_port_post_create_port, test_port_put_update_port, test_port_delete_port


@pytest.fixture
def client(sample_port1,
            sample_port2,
            sample_room1):
    from ..context import app
    from ..conftest import prep_db, close_db
    with app.app.test_client() as c:
        prep_db(
            sample_port1,
            sample_port2,
            sample_room1
        )
        yield c
        close_db()


def test_port_log_create_port(client, sample_switch1, sample_room1, caplog):
    with caplog.at_level(logging.INFO):
        test_port_post_create_port(client, sample_switch1, sample_room1)

    assert logs_contains(caplog,
                         'port_manager_update_or_create',
                         user=TESTING_CLIENT)


def test_port_log_update_port(client, sample_switch1,
                              sample_port1, caplog):
    with caplog.at_level(logging.INFO):
        test_port_put_update_port(client, sample_switch1, sample_port1)

    assert logs_contains(caplog,
                         'port_manager_update_or_create',
                         user=TESTING_CLIENT)


def test_port_log_delete_port(client, sample_switch1,
                              sample_port1, caplog):
    with caplog.at_level(logging.INFO):
        test_port_delete_port(client, sample_switch1, sample_port1)

    assert logs_contains(caplog,
                         'port_manager_delete',
                         user=TESTING_CLIENT,
                         port_id=sample_port1.id)
