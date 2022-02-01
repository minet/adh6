import json
from typing import Optional
from src.interface_adapter.sql.model.database import Database as db
from src.interface_adapter.sql.model.models import Membership
from test.integration.resource import (base_url, TEST_HEADERS)
from src.constants import MembershipStatus


def test_member_post_add_membership_not_found(api_client):
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
    result = api_client.post(
        '{}/member/{}/membership/'.format(base_url, 200),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert result.status_code == 404


def test_member_post_add_membership_bad_initial_status(api_client):
    for i in MembershipStatus:
        if i.value != "INITIAL":
            body = {
                "status": "PENDING_PAYMENT"
            }
            
            result = api_client.post(
                '{}/member/{}/membership/'.format(base_url, 1),
                data=json.dumps(body),
                content_type='application/json',
                headers=TEST_HEADERS,
            )

            membership: Optional[Membership] = db.get_db().get_session().query(Membership).filter(Membership.adherent_id == 1).one_or_none()
            
            assert result.status_code == 400
            assert membership is None