"""FastAPI router for room endpoints."""

import contextlib
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.authentication.enums import Roles
from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.database import get_session
from adh6.entity import AbstractRoom, Room
from adh6.exceptions import MemberNotFoundError, NotFoundError
from adh6.member.member_manager import MemberManager
from adh6.member.router import get_member_manager
from adh6.member.storage import MemberRepository
from adh6.security import require_role_or_ownership
from adh6.utils.filter_wrapper import AbstractRoomFilterWrapper

from .storage import RoomRepository

router = APIRouter(prefix="/room", tags=["room"])


# ============================================================================
# Dependency Injection
# ============================================================================


async def get_room_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> RoomRepository:
    """Dependency: Inject Room Repository."""
    return RoomRepository(session)


async def get_member_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MemberRepository:
    """Dependency: Inject Member Repository."""
    return MemberRepository(session)


# ============================================================================
# Room Endpoints
# ============================================================================


@router.get("")
async def search_rooms(
    repository: Annotated[RoomRepository, Depends(get_room_repository)],
    request: Request,
    response: Response,
    limit: Annotated[int, Query(ge=0)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = DEFAULT_OFFSET,
    terms: Annotated[str | None, Query()] = None,
    filter_: Annotated[AbstractRoom, AbstractRoomFilterWrapper()] = AbstractRoom(),
    only: Annotated[str | None, Query()] = None,
) -> list[Room] | list[dict]:
    """Search rooms with pagination."""
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    result, _count = await repository.search_by(limit=limit, offset=offset, terms=terms, filter_=filter_)
    response.headers["X-Total-Count"] = str(_count)
    response.headers["Access-Control-Expose-Headers"] = "X-Total-Count"

    if only:
        # Validate only fields are valid
        valid_fields = {"id", "description", "roomNumber", "vlan"}
        requested_fields = set(only.split(","))
        invalid_fields = requested_fields - valid_fields
        if invalid_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid fields: {', '.join(invalid_fields)}",
            )

        only_fields = {"id", *requested_fields}
        result = [
            {k: v for k, v in item.model_dump(mode="json", by_alias=True).items() if k in only_fields}
            for item in result
        ]

    return result  # type: ignore[return-value]


@router.post("", response_model=Room, status_code=status.HTTP_201_CREATED)
async def create_room(
    body: Room,
    repository: Annotated[RoomRepository, Depends(get_room_repository)],
    request: Request,
) -> Room:
    """Create a room."""
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    room = await repository.create(body)
    return room


@router.get("/{id}", response_model=Room)
async def get_room(
    id: int,
    repository: Annotated[RoomRepository, Depends(get_room_repository)],
    request: Request,
) -> Room:
    """Get a specific room by ID."""
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    try:
        return await repository.get_by_id(id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{id}/member", response_model=list[int])
async def list_room_members(
    id: int,
    repository: Annotated[RoomRepository, Depends(get_room_repository)],
    request: Request,
) -> list[int]:
    """List members of a room."""
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    return list(await repository.get_members(id))


@router.post("/{id}/member", status_code=status.HTTP_204_NO_CONTENT)
async def add_member_to_room(
    id: int,
    body: dict,
    repository: Annotated[RoomRepository, Depends(get_room_repository)],
    member_repository: Annotated[MemberRepository, Depends(get_member_repository)],
    member_manager: Annotated[MemberManager, Depends(get_member_manager)],
    request: Request,
) -> None:
    """Add a member to a room."""
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    try:
        member_id = int(body.get("id", -1))
        await member_repository.get_by_id(member_id)
        room = await repository.get_by_id(id)
        previous_room = await repository.get_from_member(member_id)
        if previous_room:
            await repository.remove_member(member_id)
        await repository.add_member(id, member_id)

        # Keep legacy side-effects: member subnet and device allocations depend on room assignment.
        if not previous_room:
            await member_manager.update_subnet(member_id=member_id)
            if room.vlan is not None:
                await member_manager.ethernet_vlan_changed(member_id, room.vlan)
        elif previous_room.vlan != room.vlan and room.vlan is not None:
            await member_manager.ethernet_vlan_changed(member_id, room.vlan)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_room(
    id: int,
    body: AbstractRoom,
    repository: Annotated[RoomRepository, Depends(get_room_repository)],
    member_manager: Annotated[MemberManager, Depends(get_member_manager)],
    request: Request,
) -> None:
    """Update a room."""
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    try:
        old_room = await repository.get_by_id(id)
        updated_room = await repository.update(id=id, abstract_room=body)
        if body.vlan is not None and old_room.vlan != updated_room.vlan:
            member_ids = await repository.get_members(id)
            for member_id in member_ids:
                with contextlib.suppress(MemberNotFoundError):
                    await member_manager.ethernet_vlan_changed(member_id, updated_room.vlan)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
    id: int,
    repository: Annotated[RoomRepository, Depends(get_room_repository)],
    request: Request,
) -> None:
    """Delete a room."""
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    try:
        await repository.delete(id=id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{id}/member", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member_from_room(
    id: int,
    repository: Annotated[RoomRepository, Depends(get_room_repository)],
    member_repository: Annotated[MemberRepository, Depends(get_member_repository)],
    member_manager: Annotated[MemberManager, Depends(get_member_manager)],
    request: Request,
    member_id: Annotated[int | None, Query(alias="memberId")] = None,
) -> None:
    """Remove a member from a room."""
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    if member_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="memberId is required")
    try:
        await repository.get_by_id(id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    member = await member_repository.get_by_id(member_id)
    if member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member {member_id} not found",
        )
    await repository.remove_member(member_id)
    await member_manager.reset_member(member_id)


@router.patch("/{id}/member/add", status_code=status.HTTP_204_NO_CONTENT)
async def add_member_to_room_patch(
    id: int,
    body: dict,
    repository: Annotated[RoomRepository, Depends(get_room_repository)],
    member_repository: Annotated[MemberRepository, Depends(get_member_repository)],
    member_manager: Annotated[MemberManager, Depends(get_member_manager)],
    request: Request,
) -> None:
    """Deprecated add member endpoint."""
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    member_id = int(body.get("id", -1))
    await member_repository.get_by_id(member_id)
    room = await repository.get_by_id(id)
    previous_room = await repository.get_from_member(member_id)
    if previous_room:
        await repository.remove_member(member_id)
    await repository.add_member(id, member_id)

    if not previous_room:
        await member_manager.update_subnet(member_id=member_id)
        if room.vlan is not None:
            await member_manager.ethernet_vlan_changed(member_id, room.vlan)
    elif previous_room.vlan != room.vlan and room.vlan is not None:
        await member_manager.ethernet_vlan_changed(member_id, room.vlan)


@router.patch("/{id}/member/del", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member_from_room_patch(
    id: int,
    body: dict,
    repository: Annotated[RoomRepository, Depends(get_room_repository)],
    request: Request,
) -> None:
    """Deprecated remove member endpoint."""
    require_role_or_ownership(request, Roles.NETWORK_WRITE.value)
    member_id = int(body.get("id", -1))
    await repository.get_by_id(id)
    await repository.remove_member(member_id)


@router.get("/member/{id}", response_model=int)
async def get_member_room(
    id: int,
    repository: Annotated[RoomRepository, Depends(get_room_repository)],
    request: Request,
) -> int:
    """Get room id for a member."""
    require_role_or_ownership(request, Roles.NETWORK_READ.value, id, "room")
    room = await repository.get_from_member(id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="room not found")
    if room.id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="room not found")
    return int(room.id)
