"""FastAPI router for device endpoints."""

import asyncio
import logging
from datetime import UTC, datetime
from enum import Enum
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.authentication.enums import Roles
from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.database import async_session_factory, get_session
from adh6.entity import Device, DeviceBody, DeviceFilter
from adh6.exceptions import (
    DeviceAlreadyExists,
    DevicesLimitReached,
    MemberNotFoundError,
    NotFoundError,
    RoomNotFoundError,
    ValidationError,
)
from adh6.member.storage import MemberRepository
from adh6.room.storage import RoomRepository
from adh6.security import require_role_or_ownership
from adh6.subnet.storage import VLANRepository
from adh6.subnet.vlan_manager import VlanManager
from adh6.utils.filter_wrapper import DeviceFilterWrapper

from .device_ip_manager import DeviceIpManager
from .device_manager import DeviceManager
from .netbox_sync_manager import NetboxSyncManager
from .storage import DeviceRepository, IPAllocator
from .storage.netbox_client import get_netbox_repository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/device", tags=["device"])


class NetboxSyncResponse(BaseModel):
    ips_created: int
    ips_deleted: int
    prefixes_created: int
    prefixes_deleted: int
    errors: list[str]


class NetboxSyncStatusEnum(str, Enum):
    idle = "idle"
    running = "running"
    completed = "completed"
    failed = "failed"


class NetboxSyncStatus(BaseModel):
    status: NetboxSyncStatusEnum
    started_at: datetime | None = None
    finished_at: datetime | None = None
    result: NetboxSyncResponse | None = None
    error: str | None = None


_sync_status: NetboxSyncStatus = NetboxSyncStatus(status=NetboxSyncStatusEnum.idle)
_sync_task: asyncio.Task | None = None


async def _run_sync_background() -> None:
    global _sync_status
    nb = get_netbox_repository()
    if nb is None:
        _sync_status = NetboxSyncStatus(
            status=NetboxSyncStatusEnum.failed,
            started_at=_sync_status.started_at,
            finished_at=datetime.now(UTC),
            error="Netbox integration is not enabled",
        )
        return
    try:
        async with async_session_factory() as session:
            manager = NetboxSyncManager(
                netbox_repository=nb,
                device_repository=DeviceRepository(session),
                member_repository=MemberRepository(session),
                room_repository=RoomRepository(session),
                vlan_manager=VlanManager(VLANRepository(session)),
            )
            result = await manager.sync()
        _sync_status = NetboxSyncStatus(
            status=NetboxSyncStatusEnum.completed,
            started_at=_sync_status.started_at,
            finished_at=datetime.now(UTC),
            result=NetboxSyncResponse(
                ips_created=result.ips_created,
                ips_deleted=result.ips_deleted,
                prefixes_created=result.prefixes_created,
                prefixes_deleted=result.prefixes_deleted,
                errors=result.errors,
            ),
        )
    except Exception as e:
        logger.exception("Netbox background sync failed")
        _sync_status = NetboxSyncStatus(
            status=NetboxSyncStatusEnum.failed,
            started_at=_sync_status.started_at,
            finished_at=datetime.now(UTC),
            error=str(e),
        )


def _device_to_response_dict(device: Device) -> dict[str, Any]:
    """Serialize generated OpenAPI entity with aliases expected by integration tests."""
    return device.model_dump(mode="json", by_alias=True, exclude_none=True)


def _apply_only_projection(payload: dict[str, Any], only: str | None) -> dict[str, Any]:
    """Apply legacy `only` behavior while always keeping `id`."""
    if not only:
        return payload

    wanted = {field.strip() for field in only.split(",") if field.strip()}
    wanted.add("id")
    return {k: v for k, v in payload.items() if k in wanted}


# ============================================================================
# Dependency Injection
# ============================================================================


async def get_device_manager(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> DeviceManager:
    """Dependency: Inject Device Manager with repository."""
    device_repo = DeviceRepository(session)
    device_ip_manager = DeviceIpManager(
        ip_allocator=IPAllocator(session),
        device_repository=device_repo,
        vlan_manager=VlanManager(VLANRepository(session)),
        netbox_repository=get_netbox_repository(),
    )
    member_repository = MemberRepository(session)
    room_repository = RoomRepository(session)
    return DeviceManager(
        device_repository=device_repo,
        device_ip_manager=device_ip_manager,
        member_repository=member_repository,
        room_repository=room_repository,
    )


# ============================================================================
# Device Endpoints
# ============================================================================


@router.post("", response_model=int, status_code=status.HTTP_201_CREATED)
async def create_device(
    body: DeviceBody,
    manager: Annotated[DeviceManager, Depends(get_device_manager)],
    request: Request,
) -> int:
    """Create a new device."""
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value, owner_id=body.member)
    try:
        device = await manager.create(body)
    except (MemberNotFoundError, RoomNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (ValidationError, DevicesLimitReached, DeviceAlreadyExists, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if device.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Created device has no id",
        )
    return int(device.id)


@router.get("", response_model=list[Device])
async def search_devices(
    manager: Annotated[DeviceManager, Depends(get_device_manager)],
    request: Request,
    response: Response,
    filter_: Annotated[DeviceFilter, DeviceFilterWrapper()] = DeviceFilter(),
    limit: Annotated[int, Query(ge=0)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = DEFAULT_OFFSET,
    only: Annotated[str | None, Query()] = None,
) -> Any:
    """Search devices with optional filter."""
    owner_id = filter_.member if filter_.member is not None else None
    require_role_or_ownership(request, Roles.NETWORK_READ.value, owner_id=owner_id)
    result, _count = await manager.search(limit=limit, offset=offset, device_filter=filter_)
    response.headers["X-Total-Count"] = str(_count)
    response.headers["Access-Control-Expose-Headers"] = "X-Total-Count"

    if only:
        return JSONResponse(
            content=[_apply_only_projection(_device_to_response_dict(device), only) for device in result],
            headers={
                "X-Total-Count": str(_count),
                "Access-Control-Expose-Headers": "X-Total-Count",
            },
        )
    return result


@router.get("/{id}", response_model=Device)
async def get_device(
    id: int,
    manager: Annotated[DeviceManager, Depends(get_device_manager)],
    request: Request,
    only: Annotated[str | None, Query()] = None,
) -> Any:
    """Get a specific device by ID."""
    try:
        result = await manager.get_by_id(id=id)
        require_role_or_ownership(request, Roles.NETWORK_READ.value, owner_id=result.member)
    except NotFoundError as e:
        require_role_or_ownership(
            request, Roles.NETWORK_READ.value
        )  # Check if user has read access to reveal existence of the resource
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    if only:
        return JSONResponse(content=_apply_only_projection(_device_to_response_dict(result), only))
    return result


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    id: int,
    manager: Annotated[DeviceManager, Depends(get_device_manager)],
    request: Request,
) -> None:
    """Delete a device."""
    try:
        require_role_or_ownership(request, Roles.NETWORK_WRITE.value, owner_id=await manager.get_owner(device_id=id))
        await manager.delete(id=id)
    except NotFoundError as e:
        require_role_or_ownership(
            request, Roles.NETWORK_READ.value
        )  # Check if user has read access to reveal existence of the resource
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ============================================================================
# Device Sub-Resource Endpoints
# ============================================================================


@router.get("/{id}/vendor")
async def get_device_vendor(
    id: int,
    manager: Annotated[DeviceManager, Depends(get_device_manager)],
    request: Request,
) -> str:
    """Get the MAC vendor for a device."""
    try:
        require_role_or_ownership(request, Roles.NETWORK_READ.value, owner_id=await manager.get_owner(device_id=id))
        vendor = await manager.get_mac_vendor(id=id)
    except NotFoundError as e:
        require_role_or_ownership(request, Roles.NETWORK_READ.value)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return vendor


@router.get("/{id}/mab", response_model=bool)
async def get_device_mab(
    id: int,
    manager: Annotated[DeviceManager, Depends(get_device_manager)],
    request: Request,
) -> bool:
    """Get MAB status for a device.

    Only for admins, not visible to regular users even if they own the resource"""
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    try:
        mab = await manager.get_mab(id=id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return mab


@router.post("/{id}/mab", response_model=bool)
async def set_device_mab(
    id: int,
    manager: Annotated[DeviceManager, Depends(get_device_manager)],
    request: Request,
) -> bool:
    """Set MAB for a device."""
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    try:
        mab = await manager.put_mab(id=id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return mab


@router.get("/{id}/member", response_model=int)
async def get_device_member(
    id: int,
    manager: Annotated[DeviceManager, Depends(get_device_manager)],
    request: Request,
) -> int:
    """Get the member (owner) ID for a device."""
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    try:
        owner = await manager.get_owner(device_id=id)
        if owner is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Owner for device {id} not found",
            )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return owner


@router.put("/{id}/name", status_code=status.HTTP_204_NO_CONTENT)
async def rename_device(
    id: int,
    body: dict,
    manager: Annotated[DeviceManager, Depends(get_device_manager)],
    request: Request,
) -> None:
    """Rename a device."""
    name = body.get("name")
    if not name or not isinstance(name, str):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="name is required")
    try:
        require_role_or_ownership(
            request,
            Roles.NETWORK_WRITE.value,
            owner_id=await manager.get_owner(device_id=id),
        )
        await manager.rename(device_id=id, name=name)
    except NotFoundError as e:
        require_role_or_ownership(
            request, Roles.NETWORK_READ.value
        )  # Check if user has read access to reveal existence of the resource
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{id}/wifi_password", response_model=str)
async def generate_wifi_password(
    id: int,
    manager: Annotated[DeviceManager, Depends(get_device_manager)],
    request: Request,
) -> str:
    """Generate a new random wifi password for a device."""
    require_role_or_ownership(
        request,
        Roles.NETWORK_WRITE.value,
        owner_id=await manager.get_owner(device_id=id),
    )
    try:
        return await manager.generate_wifi_password(device_id=id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{id}/wifi_password", status_code=status.HTTP_204_NO_CONTENT)
async def clear_wifi_password(
    id: int,
    manager: Annotated[DeviceManager, Depends(get_device_manager)],
    request: Request,
) -> None:
    """Clear the wifi password of a device."""
    require_role_or_ownership(
        request,
        Roles.NETWORK_WRITE.value,
        owner_id=await manager.get_owner(device_id=id),
    )
    try:
        await manager.clear_wifi_password(device_id=id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/netbox/sync", response_model=NetboxSyncStatus, status_code=status.HTTP_202_ACCEPTED)
async def sync_netbox(
    request: Request,
) -> NetboxSyncStatus:
    """Start a background Netbox IPAM reconciliation. 409 if already running."""
    global _sync_status, _sync_task
    require_role_or_ownership(request, Roles.ADMIN_WRITE.value)
    if get_netbox_repository() is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Netbox integration is not enabled",
        )
    if _sync_task is not None and not _sync_task.done():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Sync already running",
        )
    _sync_status = NetboxSyncStatus(
        status=NetboxSyncStatusEnum.running,
        started_at=datetime.now(UTC),
    )
    _sync_task = asyncio.create_task(_run_sync_background())
    return _sync_status


@router.get("/netbox/sync/status", response_model=NetboxSyncStatus, status_code=status.HTTP_200_OK)
async def get_sync_status(
    request: Request,
) -> NetboxSyncStatus:
    """Return current Netbox sync task status."""
    require_role_or_ownership(request, Roles.ADMIN_WRITE.value)
    return _sync_status
