"""FastAPI router for mini-router endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.authentication.enums import Roles
from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.database import get_session
from adh6.entity import MiniRouter, MiniRouterLoan
from adh6.exceptions import MiniRouterAlreadyExists, MiniRouterAlreadyLoaned, MiniRouterDeletionBlocked
from adh6.member.storage import MemberRepository
from adh6.security import get_user_id, require_role_or_ownership
from adh6.treasury.storage import PaymentMethodRepository

from .mini_router_manager import MiniRouterManager
from .storage import MiniRouterRepository

router = APIRouter(prefix="/mini_router", tags=["mini_router"])

CONFLICT_ERRORS = (MiniRouterAlreadyExists, MiniRouterAlreadyLoaned, MiniRouterDeletionBlocked)


async def get_mini_router_manager(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MiniRouterManager:
    """Dependency: Inject Mini-Router Manager with repositories."""
    return MiniRouterManager(
        mini_router_repository=MiniRouterRepository(session),
        member_repository=MemberRepository(session),
        payment_method_repository=PaymentMethodRepository(session),
    )


@router.get("", response_model=list[MiniRouter])
async def search_mini_routers(
    manager: Annotated[MiniRouterManager, Depends(get_mini_router_manager)],
    request: Request,
    response: Response,
    limit: Annotated[int, Query(ge=0)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = DEFAULT_OFFSET,
    terms: Annotated[str | None, Query()] = None,
    loaned: Annotated[bool | None, Query()] = None,
    overdue: Annotated[bool | None, Query()] = None,
) -> list[MiniRouter]:
    """Search mini-routers with pagination."""
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    result, count = await manager.search(limit=limit, offset=offset, terms=terms, loaned=loaned, overdue=overdue)
    response.headers["X-Total-Count"] = str(count)
    response.headers["Access-Control-Expose-Headers"] = "X-Total-Count"
    return result


@router.post("", response_model=MiniRouter, status_code=status.HTTP_201_CREATED)
async def create_mini_router(
    body: MiniRouter,
    manager: Annotated[MiniRouterManager, Depends(get_mini_router_manager)],
    request: Request,
) -> MiniRouter:
    """Create a mini-router."""
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    try:
        return await manager.create(body)
    except CONFLICT_ERRORS as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e


@router.get("/loan", response_model=list[MiniRouterLoan])
async def list_member_mini_router_loans(
    manager: Annotated[MiniRouterManager, Depends(get_mini_router_manager)],
    request: Request,
    member: Annotated[int, Query()],
) -> list[MiniRouterLoan]:
    """List the mini-router loans of a member, most recent first."""
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    return await manager.list_member_loans(member)


@router.get("/{id}", response_model=MiniRouter)
async def get_mini_router(
    id: int,
    manager: Annotated[MiniRouterManager, Depends(get_mini_router_manager)],
    request: Request,
) -> MiniRouter:
    """Get a mini-router by ID."""
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    return await manager.get_by_id(id)


@router.put("/{id}", response_model=MiniRouter)
async def update_mini_router(
    id: int,
    body: MiniRouter,
    manager: Annotated[MiniRouterManager, Depends(get_mini_router_manager)],
    request: Request,
) -> MiniRouter:
    """Update a mini-router."""
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    try:
        return await manager.update(id, body)
    except CONFLICT_ERRORS as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mini_router(
    id: int,
    manager: Annotated[MiniRouterManager, Depends(get_mini_router_manager)],
    request: Request,
) -> None:
    """Delete a mini-router and its loan history."""
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    try:
        await manager.delete(id)
    except CONFLICT_ERRORS as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e


@router.get("/{id}/loan", response_model=list[MiniRouterLoan])
async def list_mini_router_loans(
    id: int,
    manager: Annotated[MiniRouterManager, Depends(get_mini_router_manager)],
    request: Request,
) -> list[MiniRouterLoan]:
    """List the loans of a mini-router, most recent first."""
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    return await manager.list_loans(id)


@router.post("/{id}/loan", response_model=MiniRouterLoan, status_code=status.HTTP_201_CREATED)
async def create_mini_router_loan(
    id: int,
    body: MiniRouterLoan,
    manager: Annotated[MiniRouterManager, Depends(get_mini_router_manager)],
    request: Request,
) -> MiniRouterLoan:
    """Loan a mini-router to a member."""
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    author_id = get_user_id(request)
    if author_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not determine authenticated user")
    try:
        return await manager.create_loan(id, body, author_id)
    except CONFLICT_ERRORS as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e


@router.put("/loan/{id}", response_model=MiniRouterLoan)
async def update_mini_router_loan(
    id: int,
    body: MiniRouterLoan,
    manager: Annotated[MiniRouterManager, Depends(get_mini_router_manager)],
    request: Request,
) -> MiniRouterLoan:
    """Update a loan: return date, deposit status..."""
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    try:
        return await manager.update_loan(id, body)
    except CONFLICT_ERRORS as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
