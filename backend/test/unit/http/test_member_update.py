from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.authentication.enums import Roles
from adh6.authentication.keycloak_admin import KeycloakPasswordPolicyError
from adh6.authentication.middleware import authenticate
from adh6.constants import MembershipStatus
from adh6.entity import Member, Membership
from adh6.main import app
from adh6.member.interfaces import MemberRepository, MembershipRepository
from adh6.member.member_manager import MemberManager
from adh6.member.router import get_member_manager, get_password_action_client
from adh6.member.subscription_manager import SubscriptionManager
from fastapi import Request
from fastapi.testclient import TestClient

IDENTITY_EDIT = {
    "firstName": "LUC",
    "lastName": "BERNARD",
    "mail": "marbleline@minet.net",
    "username": "marbleline",
}


@pytest.fixture
def member_repository():
    member = Member(id=67, username="psders", firstName="ps", lastName="Ders", email="psders@minet.net")
    repository = MagicMock(spec=MemberRepository)
    repository.get_by_id = AsyncMock(return_value=member)
    repository.update = AsyncMock(return_value=member)
    repository.is_username_taken = AsyncMock(return_value=False)
    return repository


@pytest.fixture
def membership_repository():
    repository = MagicMock(spec=MembershipRepository)
    repository.search_by = AsyncMock(return_value=([], 0))
    return repository


@pytest.fixture
def token_info():
    return {"uid": 99, "scope": [Roles.ADMIN_WRITE.value], "auth_method": "oidc"}


@pytest.fixture
def keycloak_admin():
    client = MagicMock()
    client.send_update_password_email = AsyncMock()
    return client


@pytest.fixture
def client(monkeypatch, member_repository, membership_repository, token_info, keycloak_admin):
    subscription_manager = SubscriptionManager(
        member_repository, membership_repository, MagicMock(), MagicMock(), MagicMock()
    )
    member_manager = MemberManager(
        member_repository, MagicMock(), MagicMock(), MagicMock(), subscription_manager, MagicMock()
    )

    async def fake_authentication(request: Request):
        request.state.token_info = token_info

    monkeypatch.setitem(app.dependency_overrides, authenticate, fake_authentication)
    monkeypatch.setitem(app.dependency_overrides, get_member_manager, lambda: member_manager)
    monkeypatch.setitem(app.dependency_overrides, get_password_action_client, lambda: keycloak_admin)
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


def test_password_reset_is_delegated_to_keycloak(client, keycloak_admin):
    response = client.post("/api/member/67/password-reset")

    assert response.status_code == 204, response.text
    keycloak_admin.send_update_password_email.assert_awaited_once_with("psders")


def test_admin_password_update_is_delegated_to_keycloak(client, keycloak_admin):
    keycloak_admin.reset_password = AsyncMock()

    response = client.put("/api/member/67/password", json={"password": "ValidPassword1!"})

    assert response.status_code == 204, response.text
    keycloak_admin.reset_password.assert_awaited_once_with("psders", "ValidPassword1!")


def test_admin_password_update_returns_keycloak_policy_description(client, keycloak_admin):
    keycloak_admin.reset_password = AsyncMock(
        side_effect=KeycloakPasswordPolicyError("Invalid password: minimum length 12.")
    )

    response = client.put("/api/member/67/password", json={"password": "weak"})

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid password: minimum length 12."}


def set_membership(repository, state):
    memberships = [] if state is None else [Membership(uuid="test", member=67, status=state, hasRoom=None)]
    repository.search_by.return_value = (memberships, len(memberships))


@pytest.mark.parametrize(
    "state", [None, MembershipStatus.PENDING_RULES.value, MembershipStatus.PENDING_PAYMENT_VALIDATION.value]
)
def test_staff_can_edit_identity_without_valid_membership(client, member_repository, membership_repository, state):
    set_membership(membership_repository, state)

    response = client.patch("/api/member/67", json=IDENTITY_EDIT)

    assert response.status_code == 204, response.text
    member_repository.update.assert_awaited_once()
    updated_member = member_repository.update.call_args.args[0]
    assert updated_member.id == 67
    for field, value in IDENTITY_EDIT.items():
        entity_field = "email" if field == "mail" else field
        assert updated_member.model_dump(by_alias=True)[entity_field] == value
    membership_repository.search_by.assert_not_awaited()


@pytest.mark.parametrize("state", [None, MembershipStatus.PENDING_RULES.value])
def test_non_staff_owner_is_still_blocked_without_valid_membership(
    client, member_repository, membership_repository, token_info, state
):
    token_info.update(uid=67, scope=[Roles.USER.value])
    set_membership(membership_repository, state)

    response = client.patch("/api/member/67", json={"firstName": "Théo"})

    assert response.status_code == 400
    assert "membership not validated" in response.json()["detail"]
    member_repository.update.assert_not_awaited()


def test_non_staff_cannot_edit_someone_else(client, member_repository, token_info):
    token_info["scope"] = [Roles.USER.value]

    response = client.patch("/api/member/67", json={"firstName": "Théo"})

    assert response.status_code == 403
    member_repository.update.assert_not_awaited()


def test_client_cannot_claim_staff_exemption(client, member_repository, token_info):
    token_info.update(uid=67, scope=[Roles.USER.value])

    response = client.patch("/api/member/67", json={"firstName": "Théo", "is_staff": True})

    assert response.status_code == 400
    member_repository.update.assert_not_awaited()
