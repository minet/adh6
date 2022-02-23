# coding=utf-8
import logging
import pytest

from src.interface_adapter.http_api.auth import TESTING_CLIENT
from src.interface_adapter.sql.model.models import  db
from src.interface_adapter.sql.model.models import Switch
from test.integration.resource import logs_contains
from test.integration.test_switch import test_switch_post_valid, test_switch_update_existant_switch, \
    test_switch_delete_existant_switch


@pytest.fixture
def sample_switch():
    yield Switch(
        id=1,
        description='Switch',
        ip='192.168.102.2',
        communaute='communaute',
    )


@pytest.fixture
def client(sample_switch1):
    from ..context import app
    from ..conftest import prep_db, close_db
    with app.app.test_client() as c:
        prep_db(
            sample_switch1
        )
        yield c
        close_db()


def test_switch_log_create(client, caplog):
    with caplog.at_level(logging.INFO):
        test_switch_post_valid(client)

    log = 'TestingClient created a switch'
    assert logs_contains(caplog, 'switch_manager_update_or_create',
                         user=TESTING_CLIENT)


def test_switch_log_update(client, caplog):
    with caplog.at_level(logging.INFO):
        test_switch_update_existant_switch(client)

    assert logs_contains(caplog, 'switch_manager_update',
                         user=TESTING_CLIENT,
                         switch_id=1)


def test_switch_log_delete(client, caplog):
    with caplog.at_level(logging.INFO):
        test_switch_delete_existant_switch(client)

    assert logs_contains(caplog, 'switch_manager_delete',
                         user=TESTING_CLIENT,
                         switch_id=1)
