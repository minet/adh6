# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from datetime import datetime
from typing import List, Tuple

from sqlalchemy.orm.session import Session

from src.constants import CTX_SQL_SESSION, DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity import AbstractRoom
from src.entity.null import Null
from src.entity.room import Room
from src.exceptions import RoomNotFoundError, VLANNotFoundError
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.sql.model.models import Chambre, Vlan
from src.interface_adapter.sql.vlan_repository import _map_vlan_sql_to_entity
from src.interface_adapter.sql.track_modifications import track_modifications
from src.use_case.interface.room_repository import RoomRepository


class RoomSQLRepository(RoomRepository):

    @log_call
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None,
                  filter_: AbstractRoom = None) -> Tuple[List[Room], int]:
        session: Session = ctx.get(CTX_SQL_SESSION)

        query = session.query(Chambre)

        if filter_.id is not None:
            query = query.filter(Chambre.id == filter_.id)
        if terms:
            query = query.filter(Chambre.description.contains(terms))
        if filter_.description:
            query = query.filter(Chambre.description.contains(filter_.description))
        if filter_.room_number is not None:
            query = query.filter(Chambre.numero == filter_.room_number)


        count = query.count()
        query = query.order_by(Chambre.numero.asc())
        query = query.offset(offset)
        query = query.limit(limit)
        r = query.all()

        return list(map(_map_room_sql_to_entity, r)), count

    @log_call
    def create(self, ctx, abstract_room: Room) -> object:
        session: Session = ctx.get(CTX_SQL_SESSION)
        now = datetime.now()

        vlan = None
        if abstract_room.vlan is not None:
            vlan = session.query(Vlan).filter(Vlan.id == abstract_room.vlan).one_or_none()
            if not vlan:
                raise VLANNotFoundError(str(abstract_room.vlan))

        room = Chambre(
            numero=abstract_room.room_number,
            description=abstract_room.description,
            created_at=now,
            updated_at=now,
            vlan=vlan,
        )

        with track_modifications(ctx, session, room):
            session.add(room)
        session.flush()

        return _map_room_sql_to_entity(room)

    @log_call
    def update(self, ctx, abstract_room: AbstractRoom, override=False) -> object:
        session: Session = ctx.get(CTX_SQL_SESSION)

        query = session.query(Chambre)
        query = query.filter(Chambre.id == abstract_room.id)
        query = query.join(Vlan, Vlan.id == Chambre.vlan_id)

        room = query.one_or_none()
        if room is None:
            raise RoomNotFoundError(str(abstract_room.id))
        new_chambre = _merge_sql_with_entity(ctx, abstract_room, room, override)

        return _map_room_sql_to_entity(new_chambre)

    @log_call
    def delete(self, ctx, id) -> None:
        session: Session = ctx.get(CTX_SQL_SESSION)

        room = session.query(Chambre).filter(Chambre.id == id).one_or_none()
        if room is None:
            raise RoomNotFoundError(id)

        with track_modifications(ctx, session, room):
            session.delete(room)


def _merge_sql_with_entity(ctx, entity: AbstractRoom, sql_object: Chambre, override=False) -> Chambre:
    now = datetime.now()
    chambre = sql_object
    if entity.description is not None or override:
        chambre.description = entity.description
    if entity.room_number is not None or override:
        chambre.numero = entity.room_number
    if entity.vlan is not None:
        session: Session = ctx.get(CTX_SQL_SESSION)
        vlan = session.query(Vlan).filter(Vlan.id == entity.vlan).one_or_none()
        if not vlan:
            raise VLANNotFoundError(str(entity.vlan))
        chambre.vlan = vlan

    chambre.updated_at = now
    return chambre


def _map_room_sql_to_entity(r: Chambre) -> Room:
    return Room(
        id=r.id,
        room_number=r.numero,
        description=r.description,
        vlan=_map_vlan_sql_to_entity(r.vlan) if r.vlan is not None else Null()
    )
