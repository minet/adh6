"""FastAPI router for subnet endpoints (VLANs)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.authentication.enums import Roles
from adh6.database import get_session
from adh6.entity import Vlan
from adh6.exceptions import NotFoundError
from adh6.security import require_role_or_ownership

from .storage import VLANRepository
from .vlan_manager import VlanManager

router = APIRouter(prefix="/vlan", tags=["vlan"])


# ============================================================================
# Dependency Injection
# ============================================================================


async def get_vlan_manager(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> VlanManager:
    """Dependency: Inject VLAN Manager."""
    repo = VLANRepository(session)
    return VlanManager(repo)


# ============================================================================
# VLAN Endpoints
# ============================================================================


@router.get("", response_model=Vlan)
async def get_from_number(
    vlan_number: Annotated[int, Query()],
    manager: Annotated[VlanManager, Depends(get_vlan_manager)],
    request: Request,
) -> Vlan:
    """Get a VLAN by its number."""
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    try:
        return await manager.get_from_number(vlan_number=vlan_number)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
