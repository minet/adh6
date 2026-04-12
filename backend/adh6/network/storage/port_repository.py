"""
Implements everything related to actions on the SQL database.
"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity import AbstractPort, AbstractRoom, Port, Room, Switch
from adh6.exceptions import PortNotFoundError, RoomNotFoundError, SwitchNotFoundError
from adh6.room.storage.models import Chambre as SQLChambre

from ..interfaces import PortRepository
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

        if terms:
            stmt = stmt.where(
                (SQLPort.numero.contains(terms)) | (SQLPort.oid.contains(terms)) | (SQLPort.numero.contains(terms))
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

        # Count
        count_result = await self.session.execute(stmt)
        count = len(count_result.all())

        # Apply ordering and pagination
        stmt = stmt.order_by(SQLPort.chambre_id.asc(), SQLPort.id.asc())
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        r = result.scalars().all()

        return [_map_port_sql_to_entity(item) for item in r], count

    async def create(self, abstract_port: Port) -> Port:
        now = datetime.now()
        room = None
        switch = None

        if abstract_port.room is not None:
            stmt = select(SQLChambre).where(SQLChambre.id == abstract_port.room)
            room = await self.session.scalar(stmt)
            if not room:
                raise RoomNotFoundError(abstract_port.room)

        if abstract_port.switch_obj is not None:
            stmt = select(SQLSwitch).where(SQLSwitch.id == abstract_port.switch_obj)
            switch = await self.session.scalar(stmt)
            if not switch:
                raise SwitchNotFoundError(abstract_port.switch_obj)

        port = SQLPort(
            numero=abstract_port.port_number,
            oid=abstract_port.oid,
            switch_id=switch.id if switch else None,
            chambre_id=room.id if room else None,
            created_at=now,
            updated_at=now,
        )

        self.session.add(port)
        await self.session.flush()  # Ensure the port gets an ID
        # Map to entity while still in session context
        result = _map_port_sql_to_entity(port)

        return result

    async def update(self, object_to_update: AbstractPort, override=False) -> object:
        stmt = select(SQLPort).where(SQLPort.id == object_to_update.id)
        port = await self.session.scalar(stmt)
        if port is None:
            raise PortNotFoundError(str(object_to_update.id))
        new_port = await _merge_sql_with_entity(object_to_update, port, self.session, override)
        await self.session.flush()
        mapped_port = _map_port_sql_to_entity(new_port)

        return mapped_port

    async def delete(self, object_id) -> None:
        stmt = select(SQLPort).where(SQLPort.id == object_id)
        port = await self.session.scalar(stmt)
        if port is None:
            raise PortNotFoundError(object_id)

        await self.session.delete(port)

    async def get_rcom(self, id) -> int | None:
        stmt = select(SQLPort.rcom).where(SQLPort.id == id)
        result = await self.session.execute(stmt)
        port = result.scalar_one_or_none()
        if port is None:
            raise PortNotFoundError(id)
        return port


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
        roomObj=AbstractRoom(
            id=a.room.id,
            roomNumber=a.room.numero,
            description=a.room.description,
            vlan=a.room.vlan.numero if a.room.vlan else None,
        )
        if a.room
        else None,
    )
