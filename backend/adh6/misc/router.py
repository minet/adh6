"""FastAPI router for miscellaneous endpoints (profile, etc.)."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.database import get_session
from adh6.entity import Member, Profile200Response
from adh6.member.storage import MemberRepository

router = APIRouter(tags=["misc"])


# ============================================================================
# Dependency Injection
# ============================================================================


async def get_member_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MemberRepository:
    """Dependency: Inject member repository."""
    return MemberRepository(session)


async def get_current_user(
    request: Request,
) -> dict[str, Any]:
    """Dependency: Extract authenticated user from request context."""
    if not hasattr(request.state, "token_info"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return request.state.token_info


# ============================================================================
# Profile Endpoints
# ============================================================================


@router.get(
    "/profile", response_model=Profile200Response, status_code=status.HTTP_200_OK
)
async def get_profile(
    member_repository: Annotated[MemberRepository, Depends(get_member_repository)],
    token_info: Annotated[dict[str, Any], Depends(get_current_user)],
) -> Profile200Response:
    """
    Get current user's profile information.

    Returns the authenticated user's member data and their assigned roles.
    """
    user_id = token_info.get("uid")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    try:
        member_id = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    member = await member_repository.get_by_id(member_id)
    if member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User member record not found",
        )

    if member.id != member_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to access this resource",
        )

    roles = token_info.get("scope", [])
    return Profile200Response(member=member, roles=roles)
