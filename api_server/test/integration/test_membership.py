import json

import pytest
from adh6.member.storage.models import Adherent
from adh6.treasury.storage.models import Account, PaymentMethod
from test.integration.resource import (base_url as host_url, TEST_HEADERS)
from adh6.constants import MembershipDuration


def base_url(id) -> str:
    return f"{host_url}/member/{id}/subscription/"


@pytest.fixture
def sample_membership_pending_validation_payment_dict(sample_member: Adherent, sample_payment_method: PaymentMethod, sample_account: Account):
    yield {
        'member': sample_member.id,
        'paymentMethod': sample_payment_method.id,
        'duration': MembershipDuration.ONE_YEAR.value,
        'account': sample_account.id,
    }


@pytest.fixture
def sample_membership_not_finished_dict(sample_member: Adherent):
    yield {
        'member': sample_member.id,
    }


def test_member_post_membership(client, sample_member):
    body = {
        "account": 4,
        "duration": 0,
        "member": 4,
        "paymentMethod": 4,
    }
    result = client.post(
        base_url(sample_member.id),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert result.status_code == 200


def test_member_post_add_membership_unknown_member(client):
    body = {
        "account": 4,
        "duration": 0,
        "member": 200,
        "paymentMethod": 4,
    }
    result = client.post(
        base_url(200),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert result.status_code == 404


def test_member_post_add_membership_unknown_account(client, sample_member):
    body = {
        "account": 6969,
        "duration": 1,
        "member": sample_member.id,
        "paymentMethod": 4,
    }
    result = client.post(
        base_url(sample_member.id),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert result.status_code == 404


def test_member_post_add_membership_unknown_payment_method(client, sample_member, sample_account):
    body = {
        "account": sample_account.id,
        "duration": 1,
        "member": sample_member.id,
        "paymentMethod": 6969,
    }
    result = client.post(
        base_url(sample_member.id),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert result.status_code == 404

def test_membership_validate_membership_no_room(client, sample_room1, sample_member: Adherent, sample_membership_pending_validation_payment_dict):
    result = client.post(
        f'{host_url}/room/{sample_room1.id}/member/',
        data=json.dumps({"id": sample_member.id}),
        content_type='application/json',
        headers=TEST_HEADERS,
    )

    assert result.status_code == 204

    result = client.post(
        base_url(sample_member.id),
        data=json.dumps(sample_membership_pending_validation_payment_dict),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert result.status_code == 200

    result = client.post(
        f'{base_url(sample_member.id)}validate',
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    
    assert result.status_code == 204


def test_membership_validate_membership_not_finish(client, sample_member: Adherent, sample_membership_not_finished_dict):
    result = client.post(
        base_url(sample_member.id),
        data=json.dumps(sample_membership_not_finished_dict),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert result.status_code == 200

    result = client.post(
        f'{base_url(sample_member.id)}validate',
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    
    assert result.status_code == 400


def test_membership_patch_membership(client, sample_member: Adherent, sample_membership_not_finished_dict, sample_membership_pending_validation_payment_dict):
    result = client.post(
        base_url(sample_member.id),
        data=json.dumps(sample_membership_not_finished_dict),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert result.status_code == 200

    result = client.patch(
        base_url(sample_member.id),
        data=json.dumps(sample_membership_pending_validation_payment_dict),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    
    assert result.status_code == 204


def test_membership_multiple_subscription(client, sample_member: Adherent, sample_membership_pending_validation_payment_dict):
    result = client.post(
        base_url(sample_member.id),
        data=json.dumps(sample_membership_pending_validation_payment_dict),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert result.status_code == 200

    result = client.post(
        base_url(sample_member.id),
        data=json.dumps(sample_membership_pending_validation_payment_dict),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert result.status_code == 400
