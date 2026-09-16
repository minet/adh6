"""
Implements everything related to actions on the SQL database.
"""

from datetime import datetime
from typing import cast as typing_cast

from sqlalchemy import String, cast, func, or_, select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity import AbstractPort, AbstractRoom, Port, Room, Switch
from adh6.exceptions import (
    PortAlreadyExists,
    PortAssignmentConflict,
    PortNotFoundError,
    RoomNotFoundError,
    SwitchNotFoundError,
    UpdateImpossible,
    ValidationError,
)
from adh6.room.storage.models import Chambre as SQLChambre
from adh6.storage.count import count_rows

from ..interfaces import PortRepository
from ..port_identity import normalize_port_oid
from .models import Port as SQLPort, Switch as SQLSwitch


class PortSQLRepository(PortRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, object_id: int) -> Port:
        stmt = select(SQLPort).where(SQLPort.id == object_id)
        obj = await self.session.scalar(stmt)
        if obj is None:
            raise PortNotFoundError(object_id)
        return _map_port_sql_to_entity(obj)

    async def search_by(
        self,
        limit=DEFAULT_LIMIT,
        offset=DEFAULT_OFFSET,
        terms=None,
        filter_: AbstractPort | None = None,
    ) -> tuple[list[Port], int]:
        stmt = select(SQLPort).join(SQLSwitch, SQLSwitch.id == SQLPort.switch_id)
        stmt = stmt.outerjoin(SQLChambre, SQLChambre.id == SQLPort.chambre_id)

        terms = (terms or "").strip().lower()
        if terms:
            stmt = stmt.where(
                or_(
                    *[
                        func.lower(column).contains(terms, autoescape=True)
                        for column in [
                            SQLPort.numero,
                            SQLPort.oid,
                            SQLSwitch.description,
                            SQLSwitch.ip,
                            SQLChambre.description,
                        ]
                    ],
                    cast(SQLChambre.numero, String).startswith(terms, autoescape=True),
                )
            )
        if filter_:
            if filter_.id is not None:
                stmt = stmt.where(SQLPort.id == filter_.id)
            if filter_.port_number:
                stmt = stmt.where(SQLPort.numero.contains(filter_.port_number))
            if filter_.oid is not None:
                stmt = stmt.where(SQLPort.oid == filter_.oid)
            if filter_.room is not None:
                if isinstance(filter_.room, Room):
                    filter_.room = filter_.room.id
                stmt = stmt.where(SQLPort.chambre_id == filter_.room)
            if filter_.switch_obj is not None:
                if isinstance(filter_.switch_obj, Switch):
                    filter_.switch_obj = filter_.switch_obj.id
                stmt = stmt.where(SQLPort.switch_id == filter_.switch_obj)

        count = await count_rows(self.session, stmt)

        # Apply ordering and pagination
        stmt = stmt.order_by(SQLPort.chambre_id.asc(), SQLPort.id.asc())
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        r = result.scalars().all()

        return [_map_port_sql_to_entity(item) for item in r], count

    async def _lock_switch(self, switch_id: int | None) -> int:
        await self.session.execute(
            update(SQLSwitch).where(SQLSwitch.id == switch_id).values(updated_at=SQLSwitch.updated_at)
        )
        if await self.session.scalar(select(SQLSwitch.id).where(SQLSwitch.id == switch_id).with_for_update()) is None:
            raise SwitchNotFoundError(switch_id)
        if switch_id is None:
            raise SwitchNotFoundError(switch_id)
        return switch_id

    async def _check_identity(self, switch_id: int, oid: str | None, exclude_id: int | None = None) -> None:
        rows = await self.session.execute(
            select(SQLPort.id, SQLPort.oid).where(SQLPort.switch_id == switch_id).with_for_update()
        )
        for port_id, existing_oid in rows:
            if port_id == exclude_id:
                continue
            try:
                existing_oid = normalize_port_oid(existing_oid)
            except ValidationError:
                continue
            if existing_oid == oid:
                raise PortAlreadyExists(switch_id, existing_oid)

    async def create(self, abstract_port: AbstractPort) -> Port:
        now = datetime.now()
        room = None

        oid = abstract_port.oid
        switch_id = await self._lock_switch(abstract_port.switch_obj)
        await self._check_identity(switch_id, oid)

        if abstract_port.room is not None:
            stmt = select(SQLChambre).where(SQLChambre.id == abstract_port.room)
            room = await self.session.scalar(stmt)
            if not room:
                raise RoomNotFoundError(abstract_port.room)

        port = SQLPort(
            numero=abstract_port.port_number,
            oid=oid,
            switch_id=switch_id,
            chambre_id=room.id if room else None,
            publicly_accessible=abstract_port.publicly_accessible or False,
            created_at=now,
            updated_at=now,
        )

        # A failed bulk item must not invalidate the other successful items.
        async with self.session.begin_nested():
            self.session.add(port)
            await self.session.flush()
        # Map to entity while still in session context
        result = _map_port_sql_to_entity(port)

        return result

    async def update(self, object_to_update: AbstractPort, override=False) -> object:
        stmt = select(SQLPort).where(SQLPort.id == object_to_update.id)
        port = await self.session.scalar(stmt)
        if port is None:
            raise PortNotFoundError(str(object_to_update.id))
        switch_id = object_to_update.switch_obj if object_to_update.switch_obj is not None else port.switch_id
        oid = object_to_update.oid if object_to_update.oid is not None else ("" if override else port.oid)
        if switch_id != port.switch_id or oid != port.oid:
            locked_switches = {port.switch_id, switch_id}
            for lock_id in sorted(locked_switches):
                await self._lock_switch(lock_id)
            port = await self.session.scalar(
                select(SQLPort)
                .where(SQLPort.id == object_to_update.id)
                .with_for_update()
                .execution_options(populate_existing=True)
            )
            if port is None:
                raise PortNotFoundError(object_to_update.id)
            if port.switch_id not in locked_switches:
                raise UpdateImpossible("Port", "its switch changed concurrently; reload and retry")
            await self._check_identity(switch_id, oid, port.id)
            object_to_update.oid = oid
        new_port = await _merge_sql_with_entity(object_to_update, port, self.session, override)
        await self.session.flush()
        mapped_port = _map_port_sql_to_entity(new_port)

        return mapped_port

    async def assign_room(self, port_id: int, room_id: int | None, expected_room: int | None) -> Port:
        if room_id is not None:
            room = await self.session.scalar(select(SQLChambre).where(SQLChambre.id == room_id))
            if room is None:
                raise RoomNotFoundError(room_id)
        # Compare-and-set: a confirmation cannot overwrite a later transfer.
        result = await self.session.execute(
            update(SQLPort)
            .where(SQLPort.id == port_id, SQLPort.chambre_id == expected_room)
            .values(chambre_id=room_id, updated_at=datetime.now())
            .execution_options(synchronize_session=False)
        )
        if typing_cast(CursorResult, result).rowcount == 0:
            current = await self.session.scalar(select(SQLPort).where(SQLPort.id == port_id).with_for_update())
            if current is None:
                raise PortNotFoundError(port_id)
            if current.chambre_id != room_id:
                raise PortAssignmentConflict
        port = await self.session.scalar(
            select(SQLPort).where(SQLPort.id == port_id).execution_options(populate_existing=True)
        )
        if port is None:
            raise PortNotFoundError(port_id)
        return _map_port_sql_to_entity(port)

    async def delete(self, object_id) -> None:
        stmt = select(SQLPort).where(SQLPort.id == object_id)
        port = await self.session.scalar(stmt)
        if port is None:
            raise PortNotFoundError(object_id)

        await self.session.delete(port)


async def _merge_sql_with_entity(
    entity: AbstractPort, sql_object: SQLPort, session: AsyncSession, override=False
) -> SQLPort:
    now = datetime.now()
    port = sql_object
    if entity.oid is not None or override:
        port.oid = entity.oid or ""
    if entity.port_number is not None or override:
        port.numero = entity.port_number or ""
    if entity.room is not None:
        stmt = select(SQLChambre).where(SQLChambre.id == entity.room)
        room = await session.scalar(stmt)
        if not room:
            raise RoomNotFoundError(entity.room)
        port.chambre_id = room.id
    if entity.switch_obj is not None:
        stmt = select(SQLSwitch).where(SQLSwitch.id == entity.switch_obj)
        switch = await session.scalar(stmt)
        if not switch:
            raise SwitchNotFoundError(entity.switch_obj)
        port.switch_id = switch.id

    if entity.publicly_accessible is not None or override:
        port.publicly_accessible = entity.publicly_accessible if entity.publicly_accessible is not None else False
    port.updated_at = now
    return port


def _map_port_sql_to_entity(a: SQLPort) -> Port:
    """
    Map a Port object from SQLAlchemy to a Port (from the entity folder/layer).
    """
    return Port(
        id=a.id,
        portNumber=a.numero,
        oid=a.oid,
        room=a.chambre_id,
        switchObj=a.switch_id,
        publiclyAccessible=a.publicly_accessible,
        roomObj=AbstractRoom(
            id=a.room.id,
            roomNumber=a.room.numero,
            description=a.room.description,
            vlan=a.room.vlan.numero if a.room.vlan else None,
        )
        if a.room
        else None,
    )


def _map_port_sql_to_abstract_entity(a: SQLPort) -> AbstractPort:
    """
    Map a Port object from SQLAlchemy to a Port (from the entity folder/layer).
    """
    return AbstractPort(
        id=a.id,
        portNumber=a.numero,
        oid=a.oid,
        room=a.chambre_id,
        switchObj=a.switch_id,
        publiclyAccessible=a.publicly_accessible,
        roomObj=AbstractRoom(
            id=a.room.id,
            roomNumber=a.room.numero,
            description=a.room.description,
            vlan=a.room.vlan.numero if a.room.vlan else None,
        )
        if a.room
        else None,
    )
