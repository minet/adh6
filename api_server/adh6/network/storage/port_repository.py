# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.orm.session import Session

from adh6.constants import CTX_SQL_SESSION, DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity import AbstractPort, Port, Switch, Room
from adh6.exceptions import RoomNotFoundError, SwitchNotFoundError, PortNotFoundError
from adh6.default.decorator.log_call import log_call
from adh6.network.storage.models import Port as SQLPort, Switch as SQLSwitch
from adh6.network.interfaces.port_repository import PortRepository
from adh6.room.storage.models import Chambre as SQLChambre


class PortSQLRepository(PortRepository):
    @log_call
    def get_by_id(self, ctx, object_id: int) -> AbstractPort:
        session: Session = ctx.get(CTX_SQL_SESSION)
        obj = session.query(SQLPort).filter(SQLPort.id == object_id).one_or_none()
        if obj is None:
            raise PortNotFoundError(object_id)
        return _map_port_sql_to_abstract_entity(obj)

    @log_call
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, filter_: Optional[AbstractPort] = None) -> Tuple[List[AbstractPort], int]:
        session: Session = ctx.get(CTX_SQL_SESSION)

        query = session.query(SQLPort)
        query = query.join(SQLSwitch, SQLSwitch.id == SQLPort.switch_id)
        query = query.outerjoin(SQLChambre, SQLChambre.id == SQLPort.chambre_id)


        if terms:
            query = query.filter(SQLPort.numero.contains(terms)|
                         SQLPort.oid.contains(terms) |
                         SQLPort.numero.contains(terms))
        if filter_:
            if filter_.id is not None:
                query = query.filter(SQLPort.id == filter_.id)
            if filter_.port_number:
                query = query.filter(SQLPort.numero.contains(filter_.port_number))
            if filter_.oid is not None:
                query = query.filter(SQLPort.oid == filter_.oid)
            if filter_.room is not None:
                if isinstance(filter_.room, Room):
                    filter_.room = filter_.room.id
                query = query.filter(SQLPort.chambre_id == filter_.room)
            if filter_.switch_obj is not None:
                if isinstance(filter_.switch_obj, Switch):
                    filter_.switch_obj = filter_.switch_obj.id
                query = query.filter(SQLPort.switch_id == filter_.switch_obj)

        count = query.count()
        query = query.order_by(SQLPort.id.asc())
        query = query.offset(offset)
        query = query.limit(limit)
        r = query.all()

        return list(map(lambda item: _map_port_sql_to_abstract_entity(item), r)), count

    @log_call
    def create(self, ctx, abstract_port: Port) -> Port:
        session: Session = ctx.get(CTX_SQL_SESSION)

        now = datetime.now()

        room = None
        if abstract_port.room is not None:
            room = session.query(SQLChambre).filter(SQLChambre.id == abstract_port.room).one_or_none()
            if not room:
                raise RoomNotFoundError(abstract_port.room)

        switch = None
        if abstract_port.switch_obj is not None:
            switch = session.query(SQLSwitch).filter(SQLSwitch.id == abstract_port.switch_obj).one_or_none()
            if not switch:
                raise SwitchNotFoundError(abstract_port.switch_obj)

        port = SQLPort(
            numero=abstract_port.port_number,
            oid=abstract_port.oid,
            switch_id=switch.id if switch else None,
            chambre_id=room.id if room else None,
            created_at=now,
            updated_at=now
        )

        session.add(port)
        session.flush()

        return _map_port_sql_to_entity(port)

    @log_call
    def update(self, ctx, object_to_update: AbstractPort, override=False) -> object:
        session: Session = ctx.get(CTX_SQL_SESSION)

        query = session.query(SQLPort)
        query = query.filter(SQLPort.id == object_to_update.id)
        query = query.outerjoin(SQLChambre, SQLChambre.id == SQLPort.chambre_id)
        query = query.join(SQLSwitch, SQLSwitch.id == SQLPort.switch_id)

        port = query.one_or_none()
        if port is None:
            raise PortNotFoundError(str(object_to_update.id))
        new_port = _merge_sql_with_entity(ctx, object_to_update, port, override)

        return _map_port_sql_to_entity(new_port)

    @log_call
    def delete(self, ctx, object_id) -> None:
        session: Session = ctx.get(CTX_SQL_SESSION)

        port = session.query(SQLPort).filter(SQLPort.id == object_id).one_or_none()
        if port is None:
            raise PortNotFoundError(object_id)

        session.delete(port)
        session.flush()


    def get_rcom(self, ctx, id) -> Optional[int]:
        session: Session = ctx.get(CTX_SQL_SESSION)

        port = session.query(SQLPort.rcom).filter(SQLPort.id == id).one_or_none()
        if port is None:
            raise PortNotFoundError(id)

        return port[0]


def _merge_sql_with_entity(ctx, entity: AbstractPort, sql_object: SQLPort, override=False) -> SQLPort:
    now = datetime.now()
    port = sql_object
    if entity.oid is not None or override:
        port.oid = entity.oid
    if entity.port_number is not None or override:
        port.numero = entity.port_number
    if entity.room is not None:
        session: Session = ctx.get(CTX_SQL_SESSION)
        room = session.query(SQLChambre).filter(SQLChambre.id == entity.room).one_or_none()
        if not room:
            raise RoomNotFoundError(entity.room)
        port.chambre_id = room.id
    if entity.switch_obj is not None:
        session: Session = ctx.get(CTX_SQL_SESSION)
        switch = session.query(SQLSwitch).filter(SQLSwitch.id == entity.switch_obj).one_or_none()
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
        port_number=a.numero,
        oid=a.oid,
        room=a.chambre_id,
        switch_obj=a.switch_id
    )
def _map_port_sql_to_abstract_entity(a: SQLPort) -> AbstractPort:
    """
    Map a Port object from SQLAlchemy to a Port (from the entity folder/layer).
    """
    return AbstractPort(
        id=a.id,
        port_number=a.numero,
        oid=a.oid,
        room=a.chambre_id,
        switch_obj=a.switch_id
    )