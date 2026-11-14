# pyright: reportIncompatibleMethodOverride=false

"""
Implements everything related to actions on the SQL database.
"""

from sqlalchemy import String, cast, delete, func, insert, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.datetime_utils import utc_now_naive
from adh6.entity import AbstractRoom, Room
from adh6.exceptions import RoomNotFoundError, VLANNotFoundError
from adh6.kea.tracker import mark_member
from adh6.member.storage.models import Adherent
from adh6.room.interfaces import RoomRepository
from adh6.storage.count import count_rows
from adh6.subnet.storage.models import Vlan

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

    async def get_members(self, room_id: int) -> list[int]:
        stmt = select(RoomMemberLink.member_id).where(RoomMemberLink.room_id == room_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def remove_member(self, member_id: int) -> None:
        stmt = delete(RoomMemberLink).where(RoomMemberLink.member_id == member_id)
        await self.session.execute(stmt)
        # Without a room, Kea must no longer reserve the member's devices.
        mark_member(self.session, member_id)

        # lines needed for compatibility
        adherent_stmt = select(Adherent).where(Adherent.id == member_id)
        adherent = await self.session.scalar(adherent_stmt)
        if adherent is not None:
            stmt = update(Adherent).where(Adherent.id == adherent.id).values(chambre_id=None)
            await self.session.execute(stmt)

    async def add_member(self, room_id: int, member_id: int) -> None:
        stmt = insert(RoomMemberLink).values(member_id=member_id, room_id=room_id)
        await self.session.execute(stmt)
        mark_member(self.session, member_id)

        # Those lines are needed for compatibility
        adherent_stmt = select(Adherent).where(Adherent.id == member_id)
        adherent = await self.session.scalar(adherent_stmt)
        if adherent is not None:
            stmt = update(Adherent).where(Adherent.id == adherent.id).values(chambre_id=room_id)
            await self.session.execute(stmt)

    async def get_by_id(self, object_id: int) -> Room:
        stmt = select(Chambre).where(Chambre.id == object_id)
        obj = await self.session.scalar(stmt)
        if obj is None:
            raise RoomNotFoundError(object_id)
        return await _map_room_sql_to_entity(obj, self.session)

    async def search_by(
        self,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        terms: str | None = None,
        filter_: AbstractRoom | None = None,
    ) -> tuple[list[Room], int]:
        stmt = select(Chambre)

        terms = (terms or "").strip().lower()
        if terms:
            stmt = stmt.where(
                or_(
                    func.lower(Chambre.description).contains(terms, autoescape=True),
                    cast(Chambre.numero, String).startswith(terms, autoescape=True),
                )
            )

        if filter_:
            if filter_.id is not None:
                stmt = stmt.where(Chambre.id == filter_.id)
            if filter_.description:
                stmt = stmt.where(Chambre.description.contains(filter_.description))
            if filter_.room_number is not None:
                stmt = stmt.where(Chambre.numero == filter_.room_number)

        count = await count_rows(self.session, stmt)

        # Apply ordering and pagination
        stmt = stmt.order_by(Chambre.numero.asc(), Chambre.id.asc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        r = result.scalars().all()

        # Chambre.vlan is loaded in bulk by the selectin relationship.
        # Reuse it instead of querying the VLAN again for every search result.
        return [
            Room(
                id=room.id,
                roomNumber=room.numero or 0,
                description=room.description,
                vlan=(room.vlan.numero or 0) if room.vlan else 0,
            )
            for room in r
        ], count

    async def create(self, abstract_room: AbstractRoom) -> Room:
        now = utc_now_naive()

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
        return await _map_room_sql_to_entity(room, self.session)

    async def update(self, abstract_room: AbstractRoom, override: bool = False) -> Room:
        if abstract_room.id is None:
            raise RoomNotFoundError("missing room id")
        id = abstract_room.id
        stmt = select(Chambre).where(Chambre.id == id)
        room = await self.session.scalar(stmt)
        if room is None:
            raise RoomNotFoundError(str(abstract_room.id))
        previous_vlan_id = room.vlan_id
        new_chambre = await _merge_sql_with_entity(abstract_room, room, self.session, override)
        await self.session.flush()
        if new_chambre.vlan_id != previous_vlan_id:
            # The wired devices of the room's members change subnet.
            await self._mark_members_of(new_chambre.id)
        return await _map_room_sql_to_entity(new_chambre, self.session)

    async def delete(self, object_id: int) -> Room | None:
        stmt = select(Chambre).where(Chambre.id == object_id)
        room = await self.session.scalar(stmt)
        if room is None:
            raise RoomNotFoundError(object_id)
        # Members left without a room lose their reservations.
        await self._mark_members_of(room.id)
        await self.session.delete(room)
        return None

    async def _mark_members_of(self, room_id: int) -> None:
        """Mark the members whose adherents.chambre_id is this room, as Kea's reservations use it."""
        stmt = select(Adherent.id).where(Adherent.chambre_id == room_id)
        for member_id in (await self.session.scalars(stmt)).all():
            mark_member(self.session, member_id)


async def _merge_sql_with_entity(
    entity: AbstractRoom, sql_object: Chambre, session: AsyncSession, override: bool = False
) -> Chambre:
    now = utc_now_naive()
    chambre = sql_object
    if entity.description is not None or override:
        chambre.description = entity.description
    if entity.room_number is not None or override:
        chambre.numero = entity.room_number
    if entity.vlan is not None:
        vlan_stmt = select(Vlan).where(Vlan.numero == entity.vlan)
        vlan = await session.scalar(vlan_stmt)
        if not vlan:
            raise VLANNotFoundError(str(entity.vlan))
        chambre.vlan_id = vlan.id

    chambre.updated_at = now
    return chambre


async def _map_room_sql_to_entity(r: Chambre, session: AsyncSession) -> Room:
    stmt = select(Vlan).where(Vlan.id == r.vlan_id)
    result = await session.execute(stmt)
    vlan = result.first()
    return Room(
        id=r.id,
        roomNumber=r.numero or 0,
        description=r.description,
        vlan=vlan[0].numero or 0 if vlan else 0,
    )
