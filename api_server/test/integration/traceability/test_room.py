import logging

from test.auth import TESTING_CLIENT
from test.integration.resource import logs_contains
from test.integration.test_room import test_room_post_new_room, test_room_put_update_room, test_room_delete_existant_room


def test_room_log_create_room(client, sample_room1, caplog):
    with caplog.at_level(logging.INFO):
        test_room_post_new_room(client, sample_room1)

    assert logs_contains(caplog,
                         'room_manager_update_or_create',
                         user=TESTING_CLIENT)


def test_room_log_update_room(client, sample_room1, caplog):
    with caplog.at_level(logging.INFO):
        test_room_put_update_room(client, sample_room1)

    assert logs_contains(caplog, 'room_manager_update_or_create')


def test_room_log_delete_room(client, sample_room1, caplog):
    with caplog.at_level(logging.INFO):
        test_room_delete_existant_room(client, sample_room1)

    assert logs_contains(caplog, 'room_manager_delete')
