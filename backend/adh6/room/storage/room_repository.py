"""
Implements everything related to actions on the SQL database.
"""

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity import AbstractRoom, Room
from adh6.exceptions import RoomNotFoundError, VLANNotFoundError
from adh6.member.storage.models import Adherent
from adh6.subnet.storage.models import Vlan

from ..interfaces import RoomRepository
from .models import Chambre, RoomMemberLink


class RoomSQLRepository(RoomRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_from_member(self, member_id: int) -> Room | None:
        stmt = (
            select(Chambre)
            .join(RoomMemberLink, Chambre.id == RoomMemberLink.room_id)
            .where(RoomMemberLink.member_id == member_id)
        )

        result = await self.session.scalar(stmt)
        return await _map_room_sql_to_entity(result, self.session) if result else None

    async def get_members(self, room_id: int) -> Sequence[int]:
        stmt = select(RoomMemberLink.member_id).where(RoomMemberLink.room_id == room_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def remove_member(self, member_id: int) -> None:
        stmt = delete(RoomMemberLink).where(RoomMemberLink.member_id == member_id)
        await self.session.execute(stmt)

        # lines needed for compatibility
        adherent_stmt = select(Adherent).where(Adherent.id == member_id)
        adherent = await self.session.scalar(adherent_stmt)
        stmt = (
            update(Adherent).where(Adherent.id == adherent.id).values(chambre_id=None)
        )
        await self.session.execute(stmt)

    async def add_member(self, room_id: int, member_id: int) -> None:
        stmt = insert(RoomMemberLink).values(member_id=member_id, room_id=room_id)
        await self.session.execute(stmt)

        # Those lines are needed for compatibility
        adherent_stmt = select(Adherent).where(Adherent.id == member_id)
        adherent = await self.session.scalar(adherent_stmt)
        if adherent is not None:
            stmt = (
                update(Adherent)
                .where(Adherent.id == adherent.id)
                .values(chambre_id=room_id)
            )
            await self.session.execute(stmt)

    async def get_by_id(self, object_id: int) -> Room:
        stmt = select(Chambre).where(Chambre.id == object_id)
        obj = await self.session.scalar(stmt)
        if obj is None:
            raise RoomNotFoundError(object_id)
        return await _map_room_sql_to_entity(obj, self.session)

    async def search_by(
        self,
        limit=DEFAULT_LIMIT,
        offset=DEFAULT_OFFSET,
        terms=None,
        filter_: AbstractRoom | None = None,
    ) -> tuple[list[Room], int]:
        stmt = select(Chambre)

        if terms:
            stmt = stmt.where(Chambre.description.contains(terms))

        if filter_:
            if filter_.id is not None:
                stmt = stmt.where(Chambre.id == filter_.id)
            if filter_.description:
                stmt = stmt.where(Chambre.description.contains(filter_.description))
            if filter_.room_number is not None:
                stmt = stmt.where(Chambre.numero == filter_.room_number)

        # Count
        count_result = await self.session.execute(stmt)
        count = len(count_result.all())

        # Apply ordering and pagination
        stmt = stmt.order_by(Chambre.numero.asc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        r = result.scalars().all()

        return [await _map_room_sql_to_entity(room, self.session) for room in r], count

    async def create(self, abstract_room: Room) -> Room:
        now = datetime.now()

        vlan = None
        if abstract_room.vlan is not None:
            vlan_stmt = select(Vlan).where(Vlan.numero == abstract_room.vlan)
            vlan = await self.session.scalar(vlan_stmt)
            if not vlan:
                raise VLANNotFoundError(str(abstract_room.vlan))

        room = Chambre(
            numero=abstract_room.room_number,
            description=abstract_room.description,
            created_at=now,
            updated_at=now,
            vlan_id=vlan.id if vlan else None,
        )

        self.session.add(room)
        await self.session.flush()  # Ensure the room gets an ID
        # Map to entity while still in session context
        result = await _map_room_sql_to_entity(room, self.session)

        return result

    async def update(
        self, id: int, abstract_room: AbstractRoom, override=False
    ) -> Room:
        stmt = select(Chambre).where(Chambre.id == id)
        room = await self.session.scalar(stmt)
        if room is None:
            raise RoomNotFoundError(str(abstract_room.id))
        new_chambre = await _merge_sql_with_entity(
            abstract_room, room, self.session, override
        )
        await self.session.flush()
        mapped_room = await _map_room_sql_to_entity(new_chambre, self.session)

        return mapped_room

    async def delete(self, id) -> None:
        stmt = select(Chambre).where(Chambre.id == id)
        room = await self.session.scalar(stmt)
        if room is None:
            raise RoomNotFoundError(id)
        await self.session.delete(room)


async def _merge_sql_with_entity(
    entity: AbstractRoom, sql_object: Chambre, session: AsyncSession, override=False
) -> Chambre:
    now = datetime.now()
    chambre = sql_object
    if entity.description is not None or override:
        chambre.description = entity.description
    if entity.room_number is not None or override:
        chambre.numero = entity.room_number
    if entity.vlan is not None:
        chambre.vlan_id = entity.vlan

    chambre.updated_at = now
    return chambre


async def _map_room_sql_to_abstract_entity(
    r: Chambre, session: AsyncSession
) -> AbstractRoom:
    stmt = select(Vlan).where(Vlan.id == r.vlan_id)
    result = await session.execute(stmt)
    vlan = result.first()
    return AbstractRoom(
        id=r.id,
        roomNumber=r.numero,
        description=r.description,
        vlan=vlan[0].numero if vlan else None,
    )


async def _map_room_sql_to_entity(r: Chambre, session: AsyncSession) -> Room:
    stmt = select(Vlan).where(Vlan.id == r.vlan_id)
    result = await session.execute(stmt)
    vlan = result.first()
    return Room(
        id=r.id,
        roomNumber=r.numero,
        description=r.description,
        vlan=vlan[0].numero if vlan else None,
    )
