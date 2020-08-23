# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from datetime import datetime
from typing import List

from src.constants import CTX_SQL_SESSION, DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity import AbstractPort, Port, Switch, Room
from src.exceptions import RoomNotFoundError, SwitchNotFoundError, PortNotFoundError
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.sql.model.models import Port as SQLPort, Switch as SQLSwitch, Chambre as SQLChambre
from src.interface_adapter.sql.room_repository import _map_room_sql_to_entity
from src.interface_adapter.sql.switch_repository import _map_switch_sql_to_entity
from src.use_case.interface.port_repository import PortRepository


class PortSQLRepository(PortRepository):

    @log_call
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None,
                  filter_: AbstractPort = None) -> (List[Port], int):
        s = ctx.get(CTX_SQL_SESSION)

        q = s.query(SQLPort)
        q = q.join(SQLSwitch, SQLSwitch.id == SQLPort.switch_id)
        q = q.join(SQLChambre, SQLChambre.id == SQLPort.chambre_id)


        if terms:
            q = q.filter(SQLPort.numero.contains(terms)|
                         SQLPort.oid.contains(terms) |
                         SQLPort.numero.contains(terms))
        if filter_:
            if filter_.id is not None:
                q = q.filter(SQLPort.id == filter_.id)
            if filter_.port_number:
                q = q.filter(SQLPort.numero.contains(filter_.port_number))
            if filter_.oid is not None:
                q = q.filter(SQLPort.oid == filter_.oid)
            if filter_.room is not None:
                if isinstance(filter_.room, Room):
                    filter_.room = filter_.room.id
                q = q.filter(SQLPort.chambre_id == filter_.room)
            if filter_.switch is not None:
                if isinstance(filter_.switch, Switch):
                    filter_.switch = filter_.switch.id
                q = q.filter(SQLPort.switch_id == filter_.switch)

        count = q.count()
        q = q.order_by(SQLPort.created_at.asc())
        q = q.offset(offset)
        q = q.limit(limit)
        r = q.all()

        return list(map(lambda item: _map_port_sql_to_entity(item), r)), count

    @log_call
    def create(self, ctx, abstract_port: Port) -> object:
        s = ctx.get(CTX_SQL_SESSION)

        now = datetime.now()

        room = None
        if abstract_port.room is not None:
            room = s.query(SQLChambre).filter(SQLChambre.id == abstract_port.room).one_or_none()
            if not room:
                raise RoomNotFoundError(abstract_port.room)

        switch = None
        if abstract_port.switch is not None:
            switch = s.query(SQLSwitch).filter(SQLSwitch.id == abstract_port.switch).one_or_none()
            if not switch:
                raise SwitchNotFoundError(abstract_port.switch)

        port = SQLPort(
            numero=abstract_port.port_number,
            oid=abstract_port.oid,
            switch=switch,
            chambre=room,
            created_at=now,
            updated_at=now
        )

        s.add(port)
        s.flush()

        return _map_port_sql_to_entity(port)

    @log_call
    def update(self, ctx, object_to_update: AbstractPort, override=False) -> object:
        raise NotImplementedError

    @log_call
    def delete(self, ctx, object_id) -> None:
        s = ctx.get(CTX_SQL_SESSION)

        port = s.query(SQLPort).filter(SQLPort.id == object_id).one_or_none()
        if port is None:
            raise PortNotFoundError(object_id)

        s.delete(port)
        s.flush()


def _map_port_sql_to_entity(a: SQLPort) -> Port:
    """
    Map a Port object from SQLAlchemy to a Port (from the entity folder/layer).
    """
    return Port(
        id=a.id,
        port_number=a.numero,
        oid=a.oid,
        room=_map_room_sql_to_entity(a.chambre),
        switch=_map_switch_sql_to_entity(a.switch)
    )