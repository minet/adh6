"""FastAPI router for network endpoints (ports and switches)."""

import ipaddress
import json
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.authentication.enums import Roles
from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.database import get_session
from adh6.entity import AbstractPort, AbstractSwitch, Port, Switch
from adh6.exceptions import NotFoundError
from adh6.security import require_role_or_ownership
from adh6.utils.filter_wrapper import (
    AbstractPortFilterHandler,
    AbstractSwitchFilterHandler,
)

from .port_manager import PortManager
from .snmp import SwitchNetworkManager
from .switch_manager import SwitchManager
from .storage import PortRepository, SwitchRepository

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
        return obj.dict(by_alias=True, exclude_none=True)
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


# ============================================================================
# Port Endpoints
# ============================================================================


@port_router.get("", response_model=list[Port])
async def search_ports(
    manager: Annotated[PortManager, Depends(get_port_manager)],
    request: Request,
    filter_: Annotated[AbstractPort, AbstractPortFilterHandler()] = AbstractPort(),
    limit: Annotated[int, Query(ge=0)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = DEFAULT_OFFSET,
    terms: Annotated[str | None, Query()] = None,
    only: Annotated[str | None, Query()] = None,
) -> list[Port] | JSONResponse:
    """Search network ports."""
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    result, _count = await manager.search(
        limit=limit, offset=offset, terms=terms or "", filter_=filter_
    )

    if only:
        return JSONResponse(
            content=[
                _apply_only_projection(_to_public_dict(port), only) for port in result
            ]
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
    body: int | None,
    manager: Annotated[SwitchNetworkManager, Depends(get_switch_network_manager)],
    request: Request,
) -> None:
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    if (
        await manager.get_port_vlan(port_id=id)
    ) == "No Such Instance currently exists at this OID":
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
    filter_: Annotated[
        AbstractSwitch, AbstractSwitchFilterHandler()
    ] = AbstractSwitch(),
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
    result, _count = await manager.search(
        limit=limit, offset=offset, terms=terms or "", filter_=filter_
    )
    if only:
        return JSONResponse(
            content=[
                _apply_only_projection(_to_public_dict(switch), only)
                for switch in result
            ]
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
