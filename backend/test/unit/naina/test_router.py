from unittest.mock import AsyncMock

import pytest
from adh6.authentication.api_keys_manager import ApiKeyManager
from adh6.authentication.enums import Roles
from adh6.authentication.role_manager import RoleManager
from adh6.authentication.router import create_api_key, create_role, delete_role
from adh6.entity import ApiKeysPostRequest
from adh6.naina.manager import NainaManager
from adh6.naina.router import create_naina
from fastapi import HTTPException
from starlette.requests import Request


def _naina_request() -> Request:
    request = Request({"type": "http"})
    request.state.token_info = {
        "auth_method": "oidc",
        "scope": [
            Roles.ADMIN_READ.value,
            Roles.ADMIN_WRITE.value,
            Roles.NETWORK_READ.value,
            Roles.NETWORK_WRITE.value,
        ],
    }
    return request


async def test_naina_cannot_grant_or_refresh_naina_roles():
    manager = AsyncMock(spec=NainaManager)

    with pytest.raises(HTTPException) as exc_info:
        await create_naina("temporary-admin", manager, _naina_request())

    assert exc_info.value.status_code == 403
    manager.create.assert_not_awaited()


async def test_naina_cannot_create_permanent_roles_through_generic_endpoint():
    manager = AsyncMock(spec=RoleManager)

    with pytest.raises(HTTPException) as exc_info:
        await create_role(
            {"auth": "user", "identifier": "temporary-admin", "roles": [Roles.ADMIN_PROD.value]},
            manager,
            _naina_request(),
        )

    assert exc_info.value.status_code == 403
    manager.create.assert_not_awaited()


async def test_naina_cannot_create_a_never_expiring_api_key():
    manager = AsyncMock(spec=ApiKeyManager)
    body = ApiKeysPostRequest.model_validate({"login": "temporary-admin", "roles": [Roles.ADMIN_PROD.value]})

    with pytest.raises(HTTPException) as exc_info:
        await create_api_key(body, manager, _naina_request())

    assert exc_info.value.status_code == 403
    manager.create.assert_not_awaited()


async def test_naina_cannot_delete_permanent_roles():
    manager = AsyncMock(spec=RoleManager)

    with pytest.raises(HTTPException) as exc_info:
        await delete_role(1, manager, _naina_request())

    assert exc_info.value.status_code == 403
    manager.delete.assert_not_awaited()
