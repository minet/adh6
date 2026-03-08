"""FastAPI router for authentication endpoints (API Keys and Roles)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.authentication.enums import Roles
from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.database import get_session
from adh6.entity import ApiKey, ApiKeysPostRequest, RoleMapping
from adh6.exceptions import NotFoundError
from adh6.member.member_manager import MemberManager
from adh6.member.storage import MemberRepository
from adh6.security import get_token_info, require_role_or_ownership

from .api_keys_manager import ApiKeyManager
from .storage import ApiKeyRepository, RoleRepository
from .role_manager import RoleManager

router = APIRouter(prefix="/api_keys", tags=["api_keys"])
role_router = APIRouter(prefix="/role", tags=["authentication"])


# ============================================================================
# Dependency Injection Chain
# ============================================================================


class _MemberManagerShim(MemberManager):
    """Narrow adapter exposing only get_by_login for role/api-key managers."""

    def __init__(self, member_repo: MemberRepository):
        self._member_repo = member_repo

    async def get_by_login(self, login: str):
        return await self._member_repo.get_by_login(login)


async def get_member_manager_shim(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> _MemberManagerShim:
    """Build a lightweight member manager shim for auth dependencies."""
    return _MemberManagerShim(MemberRepository(session))


async def get_api_key_manager(
    session: Annotated[AsyncSession, Depends(get_session)],
    member_manager: Annotated[_MemberManagerShim, Depends(get_member_manager_shim)],
) -> ApiKeyManager:
    """Dependency: Inject API Key Manager with repository."""
    api_key_repo = ApiKeyRepository(session)
    role_repo = RoleRepository(session)

    return ApiKeyManager(
        api_key_repository=api_key_repo,
        role_repository=role_repo,
        member_manager=member_manager,
    )


async def get_role_manager(
    session: Annotated[AsyncSession, Depends(get_session)],
    member_manager: Annotated[_MemberManagerShim, Depends(get_member_manager_shim)],
) -> RoleManager:
    """Dependency: Inject Role Manager with repository."""
    repo = RoleRepository(session)

    return RoleManager(repo, member_manager)


# ============================================================================
# API Key Endpoints
# ============================================================================


@router.get("", response_model=list[ApiKey])
async def search_api_keys(
    manager: Annotated[ApiKeyManager, Depends(get_api_key_manager)],
    request: Request,
    limit: Annotated[int, Query(ge=0)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = DEFAULT_OFFSET,
    login: Annotated[str | None, Query()] = None,
) -> list[ApiKey]:
    """Search API keys with pagination."""
    if get_token_info(request).get("auth_method") == "api_key":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API keys cannot manage API keys")
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    result, _count = await manager.search(limit=limit, offset=offset, login=login)
    return result


@router.post("", response_model=str, status_code=status.HTTP_200_OK)
async def create_api_key(
    body: ApiKeysPostRequest,
    manager: Annotated[ApiKeyManager, Depends(get_api_key_manager)],
    request: Request,
) -> str:
    """Create a new API key.

    Return the value of the API key, not the id or login attached.
    """
    if get_token_info(request).get("auth_method") == "api_key":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API keys cannot create API keys")
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    return await manager.create(login=body.login or "", roles=body.roles or [])


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    id: int,
    manager: Annotated[ApiKeyManager, Depends(get_api_key_manager)],
    request: Request,
) -> None:
    """Delete an API key."""
    if get_token_info(request).get("auth_method") == "api_key":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API keys cannot delete API keys")
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    try:
        await manager.delete(id=id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ============================================================================
# Role Endpoints
# ============================================================================


@role_router.get("", response_model=list[RoleMapping])
async def search_roles(
    manager: Annotated[RoleManager, Depends(get_role_manager)],
    request: Request,
    auth: Annotated[str, Query(pattern="^(oidc|user|api_key)$")],
    id: Annotated[str | None, Query()] = None,
) -> list[RoleMapping]:
    """Search roles with pagination."""
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    result, _count = await manager.search(auth=auth, identifier=id)
    return result


@role_router.post("", status_code=status.HTTP_201_CREATED, response_class=Response)
async def create_role(
    body: dict,
    manager: Annotated[RoleManager, Depends(get_role_manager)],
    request: Request,
) -> Response:
    """Create a new role."""
    if get_token_info(request).get("auth_method") == "api_key":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API keys cannot create roles",
        )
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    try:
        await manager.create(
            auth=body.get("auth", "user"),
            identifier=body.get("identifier", ""),
            roles=body.get("roles", []),
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return Response(status_code=status.HTTP_201_CREATED)


@role_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    id: int,
    manager: Annotated[RoleManager, Depends(get_role_manager)],
    request: Request,
) -> None:
    """Delete a role."""
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    try:
        await manager.delete(id=id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
