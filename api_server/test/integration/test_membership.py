import json
from typing import Optional

import pytest
from src.interface_adapter.http_api.util.serializer import serialize_response
from src.interface_adapter.sql.model.models import Account, Adherent, Membership, PaymentMethod, db
from test.integration.resource import (base_url, TEST_HEADERS)
from src.constants import MembershipDuration, MembershipStatus

@pytest.fixture
def sample_membership_pending_validation_payment_dict(sample_member: Adherent, sample_payment_method: PaymentMethod, sample_account: Account):
    yield {
        'member': sample_member.id,
        'status': MembershipStatus.INITIAL.value,
        'paymentMethod': sample_payment_method.id,
        'duration': MembershipDuration.ONE_YEAR.value,
        'hasRoom': True,
        'products': [],
        'firstTime': False,
        'account': sample_account.id,
    }


def test_member_post_add_membership_not_found(client):
    body = {
        "account": 4,
        "createdAt": "2022-02-01T00:46:25.837Z",
        "duration": 0,
        "firstTime": False,
        "hasRoom": True,
        "member": 4,
        "paymentMethod": 4,
        "products": [
            1,
            2
        ],
        "status": "INITIAL",
        "updatedAt": "2022-02-01T00:46:25.837Z"
    }
    # Member with ID 200 does not exist
    result = client.post(
        '{}/member/{}/membership/'.format(base_url, 200),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert result.status_code == 404

@pytest.mark.parametrize("status,status_code", [(i.value, 400) for i in MembershipStatus if i.value != "INITIAL"] + [("INITIAL", 200)])
def test_membership_post_bad_initial_status(client, sample_member: Adherent, status: str, status_code: int):
    body = {
        "status": status,
        "member": sample_member.id
    }
    
    result = client.post(
        f'{base_url}/member/{sample_member.id}/membership/',
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS,
    )

    memberships: Optional[Membership] = db.session().query(Membership).filter(Membership.adherent_id == sample_member.id).all()
    
    assert result.status_code == status_code
    assert (len(memberships) == 1 if status_code == 400 else len(memberships) == 2)

def test_membership_validate_membership_no_room(client, sample_member: Adherent, sample_membership_pending_validation_payment_dict):
    result = client.patch(
        f'{base_url}/member/{sample_member.id}',
        data=json.dumps({
            "room": -1
        }),
        content_type='application/json',
        headers=TEST_HEADERS,
    )

    assert result.status_code == 204

    result = client.get(
        f'{base_url}/member/{sample_member.id}',
        content_type='application/json',
        headers=TEST_HEADERS,
    )

    assert result.status_code == 200
    assert "ip" not in result.json
    assert "subnet" not in result.json

    result = client.post(
        f'{base_url}/member/{sample_member.id}/membership/',
        data=json.dumps(sample_membership_pending_validation_payment_dict),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert result.status_code == 200

    result = client.get(
        f'{base_url}/member/{sample_member.id}/membership/{result.json["uuid"]}/validate',
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    
    assert result.status_code == 204
