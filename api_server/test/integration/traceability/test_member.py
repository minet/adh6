import logging

from pytest import mark

from src.interface_adapter.http_api.auth import TESTING_CLIENT
from test.integration.resource import logs_contains
from test.integration.test_member import test_member_post_member_create, test_member_put_member_update, \
    test_member_delete_existant, \
    test_member_get_logs


def test_member_log_create(api_client, sample_room1, caplog):
    with caplog.at_level(logging.INFO):
        test_member_post_member_create(api_client, sample_room1)

    assert logs_contains(
        caplog,
        'member_handler_post_called',
        user=TESTING_CLIENT
    )


def test_member_log_update(api_client, sample_member, sample_room1, caplog):
    with caplog.at_level(logging.INFO):
        test_member_put_member_update(api_client, sample_member, sample_room1)

    assert logs_contains(
        caplog,
        'member_manager_update_member_called',
        user=None,
    )


def test_member_log_delete(api_client, sample_member, caplog):
    with caplog.at_level(logging.INFO):
        test_member_delete_existant(api_client, sample_member)

    assert logs_contains(
        caplog,
        'member_manager_delete',
        user=TESTING_CLIENT,
        member_id=sample_member.id,
    )


def test_member_log_get_logs(api_client, sample_member, caplog):
    with caplog.at_level(logging.INFO):
        test_member_get_logs(api_client, sample_member)

    assert logs_contains(
        caplog,
        'member_manager_get_logs_called',
        __args=[sample_member.id],
    )
