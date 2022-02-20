import json
from typing import Optional

import pytest
from src.interface_adapter.sql.model.models import Adherent, Membership, db
from test.integration.resource import (base_url, TEST_HEADERS)
from src.constants import MembershipStatus


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

@pytest.mark.parametrize("status,status_code", [pytest.param(i.value, 400, marks=pytest.mark.xfail) for i in MembershipStatus if i.value != "INITIAL"] + [("INITIAL", 200)])
def test_membership_post_bad_initial_status(client, sample_member2: Adherent, status: str, status_code: int):
    body = {
        "status": status,
        "member": sample_member2.id
    }
    
    result = client.post(
        f'{base_url}/member/{sample_member2.id}/membership/',
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS,
    )

    membership: Optional[Membership] = db.session().query(Membership).filter(Membership.adherent_id == sample_member2.id).one_or_none()
    
    assert result.status_code == status_code
    assert (membership is None if status_code == 400 else membership is not None)
