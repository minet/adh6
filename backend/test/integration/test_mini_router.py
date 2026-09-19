from datetime import date, timedelta

import pytest
from adh6.datetime_utils import utc_today
from adh6.mini_router.storage.models import MiniRouter, MiniRouterLoan

from test import TESTING_CLIENT_ID
from test.integration.resource import (
    TEST_HEADERS,
    TEST_HEADERS_SAMPLE,
    base_url as host_url,
)

base_url = f"{host_url}/mini_router"


@pytest.fixture
def loaned_mini_router():
    return MiniRouter(
        id=1,
        hardware_mac="94:83:C4:1C:01:6E",
        number=115,
        model="beryl_giga",
        config_state="pimped",
    )


@pytest.fixture
def available_mini_router():
    return MiniRouter(
        id=2,
        hardware_mac="94:83:C4:1E:D8:31",
        model="ar750_fast",
        config_state="not_pimped",
        comment="vlan 30 -> 31 à faire",
    )


@pytest.fixture
def current_loan(loaned_mini_router, sample_member, sample_payment_method):
    return MiniRouterLoan(
        id=1,
        mini_router_id=loaned_mini_router.id,
        member_id=sample_member.id,
        started_at=date(2026, 9, 1),
        due_date=utc_today() - timedelta(days=1),
        deposit_amount=80,
        payment_method_id=sample_payment_method.id,
        deposit_status="held",
        author_id=TESTING_CLIENT_ID,
    )


@pytest.fixture
async def client(
    _test_client,
    sample_room1,
    sample_vlan,
    sample_member,
    sample_member_admin,
    sample_room_member_link,
    sample_payment_method,
    loaned_mini_router,
    available_mini_router,
    current_loan,
):
    from .conftest import add_test_fixtures, cleanup_test_data

    await add_test_fixtures(
        [sample_vlan, sample_room1, sample_member, sample_member_admin, sample_room_member_link, sample_payment_method],
        [loaned_mini_router, available_mini_router],
        current_loan,
    )

    yield _test_client

    await cleanup_test_data()


def new_mini_router(**kwargs):
    body = {
        "hardwareMac": "94-83-c4-1b-ef-22",
        "number": 117,
        "model": "beryl_giga",
        "configState": "pimped",
    }
    body.update(kwargs)
    return body


def new_loan(member_id, **kwargs):
    body = {"member": member_id, "startedAt": "2026-09-16", "depositAmount": 80, "depositStatus": "held"}
    body.update(kwargs)
    return body


class TestSearch:
    def test_all(self, client, sample_member, sample_room1):
        r = client.get(base_url, headers=TEST_HEADERS)
        assert r.status_code == 200
        assert r.headers["X-Total-Count"] == "2"
        loaned = next(m for m in r.json() if m["id"] == 1)
        assert loaned["currentLoan"]["member"] == sample_member.id
        assert loaned["currentLoan"]["memberName"] == f"{sample_member.prenom} {sample_member.nom}"
        assert loaned["roomId"] == sample_room1.id
        assert loaned["roomNumber"] == sample_room1.numero
        assert loaned["currentLoan"]["overdue"] is True
        assert loaned["currentLoan"]["miniRouterHardwareMac"] == "94:83:C4:1C:01:6E"
        assert loaned["ipWireguard"] == "10.31.0.115"
        assert loaned["ipVlan31"] == "172.30.0.115"
        assert loaned["macAccept"] == "00:00:36:00:01:15"
        assert loaned["macDeny"] == "36:36:36:00:01:15"

    @pytest.mark.parametrize(
        ("query", "expected_id"), [("loaned=true", 1), ("loaned=false", 2), ("overdue=true", 1), ("overdue=false", 2)]
    )
    def test_loaned_filter(self, client, query, expected_id):
        r = client.get(f"{base_url}?{query}", headers=TEST_HEADERS)
        assert r.status_code == 200
        assert [m["id"] for m in r.json()] == [expected_id]

    @pytest.mark.parametrize(
        ("terms", "expected_ids"),
        [
            ("d8:31", [2]),
            ("94-83", [1, 2]),
            ("dubois", [1]),
            ("5110", [1]),
            ("115", [1]),
            ("172.30.0.115", [1]),
            ("36-36-36-00-01-15", [1]),
        ],
    )
    def test_terms(self, client, terms, expected_ids):
        r = client.get(base_url, params={"terms": terms}, headers=TEST_HEADERS)
        assert r.status_code == 200
        assert [m["id"] for m in r.json()] == expected_ids

    def test_forbidden(self, client):
        assert client.get(base_url, headers=TEST_HEADERS_SAMPLE).status_code == 403


class TestCrud:
    def test_create(self, client):
        r = client.post(base_url, json=new_mini_router(), headers=TEST_HEADERS)
        assert r.status_code == 201
        assert r.json()["hardwareMac"] == "94:83:C4:1B:EF:22"
        assert client.get(f"{base_url}/{r.json()['id']}", headers=TEST_HEADERS).status_code == 200

    @pytest.mark.parametrize(
        "body",
        [new_mini_router(hardwareMac="94:83:c4:1c:01:6e"), new_mini_router(number=115)],
    )
    def test_create_duplicate(self, client, body):
        assert client.post(base_url, json=body, headers=TEST_HEADERS).status_code == 409

    @pytest.mark.parametrize(
        "body",
        [
            new_mini_router(hardwareMac="nope"),
            new_mini_router(number=0),
            new_mini_router(number=255),
            new_mini_router(model="other"),
        ],
    )
    def test_create_invalid(self, client, body):
        assert client.post(base_url, json=body, headers=TEST_HEADERS).status_code == 400

    def test_create_forbidden(self, client):
        assert client.post(base_url, json=new_mini_router(), headers=TEST_HEADERS_SAMPLE).status_code == 403

    def test_get_not_found(self, client):
        assert client.get(f"{base_url}/999", headers=TEST_HEADERS).status_code == 404

    def test_update(self, client):
        body = new_mini_router(hardwareMac="94:83:C4:1E:D8:31", comment="ok", number=None)
        r = client.put(f"{base_url}/2", json=body, headers=TEST_HEADERS)
        assert r.status_code == 200
        assert r.json()["comment"] == "ok"
        assert r.json().get("ipWireguard") is None

    def test_update_duplicate(self, client):
        body = new_mini_router(hardwareMac="94:83:C4:1C:01:6E")
        assert client.put(f"{base_url}/2", json=body, headers=TEST_HEADERS).status_code == 409

    def test_update_not_found(self, client):
        assert client.put(f"{base_url}/999", json=new_mini_router(), headers=TEST_HEADERS).status_code == 404

    def test_delete_blocked(self, client):
        assert client.delete(f"{base_url}/1", headers=TEST_HEADERS).status_code == 409

    def test_delete(self, client):
        assert client.delete(f"{base_url}/2", headers=TEST_HEADERS).status_code == 204
        assert client.get(f"{base_url}/2", headers=TEST_HEADERS).status_code == 404


class TestLoans:
    def test_list(self, client, sample_member):
        r = client.get(f"{base_url}/1/loan", headers=TEST_HEADERS)
        assert r.status_code == 200
        assert [loan["member"] for loan in r.json()] == [sample_member.id]

    def test_list_member_loans(self, client, sample_member):
        r = client.get(f"{base_url}/loan", params={"member": sample_member.id}, headers=TEST_HEADERS)
        assert r.status_code == 200
        assert [loan["miniRouter"] for loan in r.json()] == [1]
        assert client.get(f"{base_url}/loan", params={"member": 999999}, headers=TEST_HEADERS).json() == []

    def test_list_member_loans_forbidden(self, client, sample_member):
        r = client.get(f"{base_url}/loan", params={"member": sample_member.id}, headers=TEST_HEADERS_SAMPLE)
        assert r.status_code == 403

    def test_list_not_found(self, client):
        assert client.get(f"{base_url}/999/loan", headers=TEST_HEADERS).status_code == 404

    def test_create(self, client, sample_member, sample_payment_method):
        body = new_loan(sample_member.id, paymentMethod=sample_payment_method.id, dueDate="2027-06-30")
        r = client.post(f"{base_url}/2/loan", json=body, headers=TEST_HEADERS)
        assert r.status_code == 201
        assert r.json()["miniRouter"] == 2
        assert r.json()["author"] == TESTING_CLIENT_ID
        assert r.json()["authorName"] is not None
        assert r.json()["overdue"] is False
        assert client.get(f"{base_url}/2", headers=TEST_HEADERS).json()["currentLoan"]["id"] == r.json()["id"]

    def test_create_forces_held_deposit(self, client, sample_member):
        body = new_loan(sample_member.id, depositStatus="refunded")
        r = client.post(f"{base_url}/2/loan", json=body, headers=TEST_HEADERS)
        assert r.status_code == 201
        assert r.json()["depositStatus"] == "held"

    def test_create_without_deposit_status(self, client, sample_member):
        body = new_loan(sample_member.id)
        del body["depositStatus"]
        r = client.post(f"{base_url}/2/loan", json=body, headers=TEST_HEADERS)
        assert r.status_code == 201
        assert r.json()["depositStatus"] == "held"

    def test_create_already_loaned(self, client, sample_member):
        r = client.post(f"{base_url}/1/loan", json=new_loan(sample_member.id), headers=TEST_HEADERS)
        assert r.status_code == 409

    def test_create_unknown_member(self, client):
        assert client.post(f"{base_url}/2/loan", json=new_loan(999999), headers=TEST_HEADERS).status_code == 404

    def test_create_unknown_payment_method(self, client, sample_member):
        body = new_loan(sample_member.id, paymentMethod=999)
        assert client.post(f"{base_url}/2/loan", json=body, headers=TEST_HEADERS).status_code == 404

    def test_returned_with_deposit_held(self, client, sample_member):
        body = new_loan(sample_member.id, startedAt="2026-09-01", returnedAt="2026-09-15")
        assert client.put(f"{base_url}/loan/1", json=body, headers=TEST_HEADERS).status_code == 200
        mini_router = client.get(f"{base_url}/1", headers=TEST_HEADERS).json()
        assert mini_router["depositToRefund"] is True
        assert client.delete(f"{base_url}/1", headers=TEST_HEADERS).status_code == 409

    def test_return_then_delete(self, client, sample_member):
        body = new_loan(sample_member.id, startedAt="2026-09-01", returnedAt="2026-09-15", depositStatus="refunded")
        r = client.put(f"{base_url}/loan/1", json=body, headers=TEST_HEADERS)
        assert r.status_code == 200
        assert r.json()["returnedAt"] == "2026-09-15"

        mini_router = client.get(f"{base_url}/1", headers=TEST_HEADERS).json()
        assert mini_router.get("currentLoan") is None
        assert mini_router.get("roomId") is None
        assert mini_router["depositToRefund"] is False
        assert client.delete(f"{base_url}/1", headers=TEST_HEADERS).status_code == 204

    def test_update_invalid_dates(self, client, sample_member):
        body = new_loan(sample_member.id, startedAt="2026-09-01", returnedAt="2026-08-01")
        assert client.put(f"{base_url}/loan/1", json=body, headers=TEST_HEADERS).status_code == 400

    def test_update_not_found(self, client, sample_member):
        assert (
            client.put(f"{base_url}/loan/999", json=new_loan(sample_member.id), headers=TEST_HEADERS).status_code == 404
        )

    def test_update_forbidden(self, client, sample_member):
        r = client.put(f"{base_url}/loan/1", json=new_loan(sample_member.id), headers=TEST_HEADERS_SAMPLE)
        assert r.status_code == 403
