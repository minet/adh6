import logging
import pytest

from test.auth import TESTING_CLIENT
from test.integration.resource import TEST_HEADERS, logs_contains


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
        from test.integration.test_port import test_port_post_create_port
        test_port_post_create_port(client, sample_switch1, sample_room1, TEST_HEADERS, 201)

    assert logs_contains(caplog, 'port_manager_update_or_create')


def test_port_log_update_port(client, sample_switch1, sample_port1, caplog):
    with caplog.at_level(logging.INFO):
        from test.integration.test_port import test_port_put_update_port
        test_port_put_update_port(client, sample_switch1, sample_port1, sample_port1.id, None, None, TEST_HEADERS, None, 204)

    assert logs_contains(caplog, 'port_manager_update_or_create')


def test_port_log_delete_port(client, sample_port1, caplog):
    with caplog.at_level(logging.INFO):
        from test.integration.test_port import test_port_delete_port
        test_port_delete_port(client, sample_port1.id, 204, TEST_HEADERS, None)

    assert logs_contains(caplog, 'port_manager_delete')
