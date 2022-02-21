import logging

from pytest import mark

from src.interface_adapter.http_api.auth import TESTING_CLIENT
from test.integration.resource import logs_contains


def test_member_log_create(client, sample_room1, caplog):
    with caplog.at_level(logging.INFO):
        from test.integration.test_member import test_member_post_member_create
        test_member_post_member_create(client, sample_room1)

    assert logs_contains(
        caplog,
        'member_handler_post_called',
        user=TESTING_CLIENT
    )


def test_member_log_update(client, sample_member, sample_room1, caplog):
    with caplog.at_level(logging.INFO):
        from test.integration.test_member import test_member_put_member_update
        test_member_put_member_update(client, sample_member, sample_room1)

    assert logs_contains(
        caplog,
        'member_manager_update_member_called',
        user=None,
    )


def test_member_log_delete(client, sample_member, caplog):
    with caplog.at_level(logging.INFO):
        from test.integration.test_member import test_member_delete_existant
        test_member_delete_existant(client, sample_member)

    assert logs_contains(
        caplog,
        'member_manager_delete',
        user=TESTING_CLIENT,
        member_id=sample_member.id,
    )


def test_member_log_get_logs(client, sample_member, caplog):
    with caplog.at_level(logging.INFO):
        from test.integration.test_member import test_member_get_logs
        test_member_get_logs(client, sample_member)

    assert logs_contains(
        caplog,
        'member_manager_get_logs_called',
        __args=[sample_member.id],
    )
