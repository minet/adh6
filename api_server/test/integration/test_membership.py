import json

import pytest
from adh6.storage.sql.models import Account, Adherent, PaymentMethod
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


def test_member_post_add_membership_not_found(client):
    body = {
        "account": 4,
        "duration": 0,
        "member": 4,
        "paymentMethod": 4,
    }
    # Member with ID 200 does not exist
    result = client.post(
        base_url(200),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert result.status_code == 404

def test_membership_validate_membership_no_room(client, sample_member: Adherent, sample_membership_pending_validation_payment_dict):
    result = client.patch(
        f'{host_url}/member/{sample_member.id}',
        data=json.dumps({
            "roomNumber": -1
        }),
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
