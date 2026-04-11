"""FastAPI router for network endpoints (ports and switches)."""

import ipaddress
from typing import Annotated, Any

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.authentication.enums import Roles
from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.database import get_session
from adh6.entity import (
    AbstractPort,
    AbstractRoom,
    AbstractSwitch,
    BulkOperationResult,
    DiscoveredPort,
    PingRequest,
    PingResult,
    Port,
    Switch,
)
from adh6.exceptions import NetworkManagerReadError, NotFoundError
from adh6.room.storage import RoomRepository as RoomStorageRepository
from adh6.security import require_role_or_ownership
from adh6.utils.filter_wrapper import (
    AbstractPortFilterHandler,
    AbstractSwitchFilterHandler,
)

from .port_manager import PortManager
from .snmp import SwitchNetworkManager
from .storage import PortRepository, SwitchRepository
from .switch_manager import SwitchManager

port_router = APIRouter(prefix="/port", tags=["port"])
switch_router = APIRouter(prefix="/switch", tags=["switch"])

SWITCH_VALID_FIELDS = {"id", "ip", "description"}


def _validate_ipv4(ip: str | None) -> None:
    if ip is None:
        return
    try:
        ipaddress.IPv4Address(ip)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid IPv4 address: {ip}",
        )


def _to_public_dict(obj: Any) -> dict[str, Any]:
    if hasattr(obj, "dict"):
        return obj.model_dump(by_alias=True, exclude_none=True)
    return dict(obj)


def _apply_only_projection(payload: dict[str, Any], only: str | None) -> dict[str, Any]:
    if not only:
        return payload

    wanted = {field.strip() for field in only.split(",") if field.strip()}
    wanted.add("id")
    return {k: v for k, v in payload.items() if k in wanted}


# ============================================================================
# Dependency Injection
# ============================================================================


async def get_port_manager(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> PortManager:
    """Dependency: Inject Port Manager."""
    repo = PortRepository(session)
    return PortManager(repo)


async def get_switch_manager(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SwitchManager:
    """Dependency: Inject Switch Manager."""
    repo = SwitchRepository(session)
    return SwitchManager(repo)


async def get_switch_network_manager(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SwitchNetworkManager:
    """Dependency: Inject switch network manager."""
    return SwitchNetworkManager(PortRepository(session), SwitchRepository(session))


async def get_switch_bulk_deps(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> tuple[SwitchNetworkManager, PortManager, RoomStorageRepository]:
    """Dependency: Inject network manager, port manager and room repository for bulk ops."""
    net_manager = SwitchNetworkManager(PortRepository(session), SwitchRepository(session))
    port_manager = PortManager(PortRepository(session))
    room_repo = RoomStorageRepository(session)
    return net_manager, port_manager, room_repo


# ============================================================================
# Port Endpoints
# ============================================================================


@port_router.get("", response_model=list[Port])
async def search_ports(
    manager: Annotated[PortManager, Depends(get_port_manager)],
    request: Request,
    response: Response,
    filter_: Annotated[AbstractPort, AbstractPortFilterHandler()] = AbstractPort(),
    limit: Annotated[int, Query(ge=0)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = DEFAULT_OFFSET,
    terms: Annotated[str | None, Query()] = None,
    only: Annotated[str | None, Query()] = None,
) -> list[Port] | JSONResponse:
    """Search network ports."""
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    result, _count = await manager.search(limit=limit, offset=offset, terms=terms or "", filter_=filter_)
    response.headers["X-Total-Count"] = str(_count)

    if only:
        return JSONResponse(
            content=[_apply_only_projection(_to_public_dict(port), only) for port in result],
            headers={"X-Total-Count": str(_count)},
        )
    return result


@port_router.post("", response_model=Port, status_code=status.HTTP_201_CREATED)
async def create_port(
    body: AbstractPort,
    manager: Annotated[PortManager, Depends(get_port_manager)],
    request: Request,
) -> Port:
    """Create a network port."""
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    port = await manager.create(body)
    return port


@port_router.post("/bulk", response_model=BulkOperationResult)
async def bulk_create_ports(
    bodies: list[AbstractPort],
    manager: Annotated[PortManager, Depends(get_port_manager)],
    request: Request,
) -> BulkOperationResult:
    """Bulk create network ports."""
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    data = await manager.bulk_create(bodies)
    return BulkOperationResult(**data)


@port_router.get("/{id}", response_model=Port)
async def get_port(
    id: int,
    manager: Annotated[PortManager, Depends(get_port_manager)],
    request: Request,
) -> Port:
    """Get a specific port by ID."""
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    try:
        return await manager.get_by_id(id=id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@port_router.put("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_port(
    id: int,
    body: AbstractPort,
    manager: Annotated[PortManager, Depends(get_port_manager)],
    request: Request,
) -> None:
    """Update a network port."""
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    try:
        await manager.update(id, body)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@port_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_port(
    id: int,
    manager: Annotated[PortManager, Depends(get_port_manager)],
    request: Request,
) -> None:
    """Delete a network port."""
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    try:
        await manager.delete(id=id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@port_router.get("/{id}/state", response_model=bool)
async def get_port_state(
    id: int,
    manager: Annotated[SwitchNetworkManager, Depends(get_switch_network_manager)],
    request: Request,
) -> bool:
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    return (await manager.get_port_status(port_id=id)) == "up"


@port_router.put("/{id}/state", response_model=bool)
async def toggle_port_state(
    id: int,
    manager: Annotated[SwitchNetworkManager, Depends(get_switch_network_manager)],
    request: Request,
) -> bool:
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    return (await manager.update_port_status(port_id=id)) == "up"


@port_router.get("/{id}/vlan", response_model=int)
async def get_port_vlan(
    id: int,
    manager: Annotated[SwitchNetworkManager, Depends(get_switch_network_manager)],
    request: Request,
) -> int:
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    value = await manager.get_port_vlan(port_id=id)
    if value == "No Such Instance currently exists at this OID":
        return 1
    return int(value)


@port_router.put("/{id}/vlan", status_code=status.HTTP_204_NO_CONTENT)
async def set_port_vlan(
    id: int,
    body: Annotated[int | None, Body()],
    manager: Annotated[SwitchNetworkManager, Depends(get_switch_network_manager)],
    request: Request,
) -> None:
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    if (await manager.get_port_vlan(port_id=id)) == "No Such Instance currently exists at this OID":
        return
    await manager.update_port_vlan(
        port_id=id,
        elevated=lambda: require_role_or_ownership(request, Roles.ADMIN_WRITE.value),
        vlan=int(body) if body is not None else 1,
    )


@port_router.get("/{id}/mab", response_model=bool)
async def get_port_mab(
    id: int,
    manager: Annotated[SwitchNetworkManager, Depends(get_switch_network_manager)],
    request: Request,
) -> bool:
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    return (await manager.get_port_mab(port_id=id)) == "true"


@port_router.put("/{id}/mab", response_model=bool)
async def set_port_mab(
    id: int,
    manager: Annotated[SwitchNetworkManager, Depends(get_switch_network_manager)],
    request: Request,
) -> bool:
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    return (await manager.update_port_mab(port_id=id)) == "true"


@port_router.get("/{id}/auth", response_model=bool)
async def get_port_auth(
    id: int,
    manager: Annotated[SwitchNetworkManager, Depends(get_switch_network_manager)],
    request: Request,
) -> bool:
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    return (await manager.get_port_auth(port_id=id)) == "auto"


@port_router.put("/{id}/auth", response_model=bool)
async def set_port_auth(
    id: int,
    manager: Annotated[SwitchNetworkManager, Depends(get_switch_network_manager)],
    request: Request,
) -> bool:
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    return (await manager.update_port_auth(port_id=id)) == "auto"


@port_router.get("/{id}/use", response_model=str)
async def get_port_use(
    id: int,
    manager: Annotated[SwitchNetworkManager, Depends(get_switch_network_manager)],
    request: Request,
) -> str:
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    return str(await manager.get_port_use(port_id=id))


@port_router.get("/{id}/alias", response_model=str)
async def get_port_alias(
    id: int,
    manager: Annotated[SwitchNetworkManager, Depends(get_switch_network_manager)],
    request: Request,
) -> str:
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    return str(await manager.get_port_alias(port_id=id))


@port_router.get("/{id}/speed", response_model=str)
async def get_port_speed(
    id: int,
    manager: Annotated[SwitchNetworkManager, Depends(get_switch_network_manager)],
    request: Request,
) -> str:
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    return str(await manager.get_port_speed(port_id=id))


# ============================================================================
# Switch Endpoints
# ============================================================================


@switch_router.get("", response_model=list[Switch])
async def search_switches(
    manager: Annotated[SwitchManager, Depends(get_switch_manager)],
    request: Request,
    response: Response,
    filter_: Annotated[AbstractSwitch, AbstractSwitchFilterHandler()] = AbstractSwitch(),
    limit: Annotated[int, Query(ge=0)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = DEFAULT_OFFSET,
    terms: Annotated[str | None, Query()] = None,
    only: Annotated[str | None, Query()] = None,
) -> list[Switch] | JSONResponse:
    """Search network switches."""
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    if only:
        requested = {field.strip() for field in only.split(",") if field.strip()}
        invalid = requested - SWITCH_VALID_FIELDS
        if invalid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid only fields: {invalid}",
            )
    result, _count = await manager.search(limit=limit, offset=offset, terms=terms or "", filter_=filter_)
    response.headers["X-Total-Count"] = str(_count)
    if only:
        return JSONResponse(
            content=[_apply_only_projection(_to_public_dict(switch), only) for switch in result],
            headers={"X-Total-Count": str(_count)},
        )
    return result


@switch_router.post("", response_model=Switch, status_code=status.HTTP_201_CREATED)
async def create_switch(
    body: AbstractSwitch,
    manager: Annotated[SwitchManager, Depends(get_switch_manager)],
    request: Request,
) -> Switch:
    """Create a network switch."""
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    _validate_ipv4(body.ip)
    switch = await manager.create(body)
    return switch


@switch_router.get("/{id}", response_model=Switch)
async def get_switch(
    id: int,
    manager: Annotated[SwitchManager, Depends(get_switch_manager)],
    request: Request,
) -> Switch:
    """Get a specific switch by ID."""
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    try:
        return await manager.get_by_id(id=id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@switch_router.put("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_switch(
    id: int,
    body: AbstractSwitch,
    manager: Annotated[SwitchManager, Depends(get_switch_manager)],
    request: Request,
) -> None:
    """Update a network switch."""
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    _validate_ipv4(body.ip)
    try:
        await manager.update(id, body)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@switch_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_switch(
    id: int,
    manager: Annotated[SwitchManager, Depends(get_switch_manager)],
    request: Request,
) -> None:
    """Delete a network switch."""
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    try:
        await manager.delete(id=id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ============================================================================
# Switch Bulk Action Endpoints
# ============================================================================


@switch_router.post("/{id}/apply-descriptions", response_model=BulkOperationResult)
async def apply_port_descriptions(
    id: int,
    deps: Annotated[tuple, Depends(get_switch_bulk_deps)],
    request: Request,
) -> BulkOperationResult:
    """Set each port SNMP alias (IF-MIB::ifAlias) to its linked room description."""
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    net_manager, port_manager, room_repo = deps
    try:
        await net_manager.switch_repository.get_by_id(object_id=id)  # type: ignore[attr-defined]
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    ports, _ = await port_manager.search(limit=500, offset=0, terms="", filter_=AbstractPort(switchObj=id))
    success, failed, errors = 0, 0, []
    for port in ports:
        if port.room is None:
            continue
        try:
            room = await room_repo.get_by_id(object_id=port.room)
            alias = room.description or f"Room {room.room_number}"
            await net_manager.update_port_alias(port_id=port.id, alias=alias)  # type: ignore[arg-type]
            success += 1
        except Exception as e:
            failed += 1
            errors.append(f"Port {port.port_number}: {e}")
    return BulkOperationResult(success=success, failed=failed, errors=errors)


@switch_router.post("/{id}/apply-vlans", response_model=BulkOperationResult)
async def apply_port_vlans(
    id: int,
    vlan: Annotated[int, Body()],
    deps: Annotated[tuple, Depends(get_switch_bulk_deps)],
    request: Request,
) -> BulkOperationResult:
    """Assign a VLAN number to all rooms linked to ports on this switch (database only, no SNMP)."""
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    net_manager, port_manager, room_repo = deps
    try:
        await net_manager.switch_repository.get_by_id(object_id=id)  # type: ignore[attr-defined]
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    ports, _ = await port_manager.search(limit=500, offset=0, terms="", filter_=AbstractPort(switchObj=id))
    # Deduplicate room IDs so each room is updated exactly once
    seen_rooms: set[int] = set()
    success, failed, errors = 0, 0, []
    for port in ports:
        if port.room is None or port.room in seen_rooms:
            continue
        seen_rooms.add(port.room)
        try:
            await room_repo.update(port.room, AbstractRoom(vlan=vlan))
            success += 1
        except Exception as e:
            failed += 1
            errors.append(f"Room {port.room}: {e}")
    return BulkOperationResult(success=success, failed=failed, errors=errors)


@switch_router.post("/{id}/ping", response_model=PingResult)
async def ping_switch(
    id: int,
    body: PingRequest,
    net_manager: Annotated[SwitchNetworkManager, Depends(get_switch_network_manager)],
    request: Request,
) -> PingResult:
    """Run an ICMP ping from the switch via Cisco SNMP Ping MIB."""
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    _validate_ipv4(body.address)
    try:
        data = await net_manager.ping_from_switch(
            switch_id=id,
            address=body.address,
            count=body.count or 5,
            timeout_ms=body.timeout_ms or 2000,
            size=body.size or 100,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NetworkManagerReadError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
    return PingResult(**data)


@switch_router.get("/{id}/discover-ports", response_model=list[DiscoveredPort])
async def discover_ports(
    id: int,
    manager: Annotated[SwitchNetworkManager, Depends(get_switch_network_manager)],
    request: Request,
) -> list[DiscoveredPort]:
    """Discover ports on a switch via SNMP."""
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    try:
        data = await manager.discover_ports(switch_id=id)
        return [DiscoveredPort(**item) for item in data]
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NetworkManagerReadError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


@switch_router.post("/{id}/sync-port-names", response_model=BulkOperationResult)
async def sync_port_names(
    id: int,
    manager: Annotated[SwitchNetworkManager, Depends(get_switch_network_manager)],
    request: Request,
) -> BulkOperationResult:
    """Sync port names from switch technical names via SNMP."""
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    try:
        data = await manager.sync_port_names(switch_id=id)
        return BulkOperationResult(**data)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NetworkManagerReadError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
