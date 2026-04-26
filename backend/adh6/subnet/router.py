"""FastAPI router for subnet endpoints (VLANs)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.authentication.enums import Roles
from adh6.database import get_session
from adh6.entity import AbstractVlan, VlanStats
from adh6.exceptions import NotFoundError
from adh6.security import require_role_or_ownership

from .storage import VLANRepository
from .vlan_manager import VlanManager

router = APIRouter(prefix="/vlan", tags=["vlan"])
vlans_router = APIRouter(prefix="/vlans", tags=["vlan"])


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


@router.get("", response_model=AbstractVlan)
async def get_from_number(
    vlan_number: Annotated[int, Query()],
    manager: Annotated[VlanManager, Depends(get_vlan_manager)],
    request: Request,
) -> AbstractVlan:
    """Get a VLAN by its number."""
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    try:
        return await manager.get_from_number(vlan_number=vlan_number)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@vlans_router.get("", response_model=list[AbstractVlan])
async def vlans_get(
    manager: Annotated[VlanManager, Depends(get_vlan_manager)],
    request: Request,
) -> list[AbstractVlan]:
    """List all VLANs."""
    require_role_or_ownership(request, Roles.ADMIN_READ.value)
    return await manager.list_vlans()


@vlans_router.get("/stats", response_model=list[VlanStats])
async def vlans_stats_get(
    manager: Annotated[VlanManager, Depends(get_vlan_manager)],
    request: Request,
) -> list[VlanStats]:
    """List all VLANs with device counts and over-limit devices."""
    require_role_or_ownership(request, Roles.ADMIN_READ.value)
    return await manager.get_stats()
