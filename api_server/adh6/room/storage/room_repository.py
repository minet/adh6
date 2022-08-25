# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from datetime import datetime
from typing import List, Optional, Tuple, Union
from sqlalchemy import insert, select, delete, update

from sqlalchemy.orm.session import Session

from adh6.constants import CTX_SQL_SESSION, DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity import AbstractRoom, Room
from adh6.exceptions import RoomNotFoundError, VLANNotFoundError
from adh6.default.decorator.log_call import log_call
from adh6.storage.sql.models import Adherent, Chambre, Vlan, RoomMemberLink
from adh6.storage.sql.track_modifications import track_modifications
from adh6.room.interfaces.room_repository import RoomRepository


class RoomSQLRepository(RoomRepository):
    def get_from_member(self, ctx, member_id: int) -> Union[Room, None]:
        session: Session = ctx.get(CTX_SQL_SESSION)
        smt = select(Chambre)\
            .join(RoomMemberLink, Chambre.id == RoomMemberLink.room_id)\
            .where(RoomMemberLink.member_id == member_id)
        
        result = session.execute(smt).scalar_one_or_none()

        return _map_room_sql_to_entity(result) if result else None

    def get_members(self, ctx, room_id: int) -> List[int]:
        session: Session = ctx.get(CTX_SQL_SESSION)
        smt = select(RoomMemberLink.member_id).where(RoomMemberLink.room_id == room_id)
        return session.execute(smt).scalars().all()

    def remove_member(self, ctx, member_id: int) -> None:
        session: Session = ctx.get(CTX_SQL_SESSION)
        smt = delete(RoomMemberLink).where(RoomMemberLink.member_id == member_id)
        session.execute(smt)

        # lines needed for compatibility
        adherent = session.query(Adherent).filter(Adherent.id == member_id).one()
        smt = update(Adherent).where(Adherent.id == adherent.id).values(chambre_id=None)
        session.execute(smt)

    def add_member(self, ctx, room_id: int, member_id: int) -> None:
        session: Session = ctx.get(CTX_SQL_SESSION)
        smt = insert(RoomMemberLink).values(
            member_id=member_id,
            room_id=room_id
        )
        session.execute(smt)

        # Those lines are needed for compatibility
        adherent = session.query(Adherent).filter(Adherent.id == member_id).one()
        smt = update(Adherent).where(Adherent.id == adherent.id).values(chambre_id=room_id)
        session.execute(smt)

    @log_call
    def get_by_id(self, ctx, object_id: int) -> AbstractRoom:
        session: Session = ctx.get(CTX_SQL_SESSION)
        obj = session.query(Chambre).filter(Chambre.id == object_id).one_or_none()
        if obj is None:
            raise RoomNotFoundError(object_id)
        return _map_room_sql_to_abstract_entity(obj)

    @log_call
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, filter_: Optional[AbstractRoom] = None) -> Tuple[List[AbstractRoom], int]:
        session: Session = ctx.get(CTX_SQL_SESSION)

        query = session.query(Chambre)

        if terms:
            query = query.filter(Chambre.description.contains(terms))

        if filter_:
            if filter_.id is not None:
                query = query.filter(Chambre.id == filter_.id)
            if filter_.description:
                query = query.filter(Chambre.description.contains(filter_.description))
            if filter_.room_number is not None:
                query = query.filter(Chambre.numero == filter_.room_number)


        count = query.count()
        query = query.order_by(Chambre.numero.asc())
        query = query.offset(offset)
        query = query.limit(limit)
        r = query.all()

        return list(map(_map_room_sql_to_abstract_entity, r)), count

    @log_call
    def create(self, ctx, abstract_room: Room) -> Room:
        session: Session = ctx.get(CTX_SQL_SESSION)
        now = datetime.now()

        vlan = None
        if abstract_room.vlan is not None:
            vlan = session.query(Vlan).filter(Vlan.numero == abstract_room.vlan).one_or_none()
            if not vlan:
                raise VLANNotFoundError(str(abstract_room.vlan))

        room = Chambre(
            numero=abstract_room.room_number,
            description=abstract_room.description,
            created_at=now,
            updated_at=now,
            vlan_id=vlan.id if vlan else None,
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
        vlan = session.query(Vlan).filter(Vlan.numero == entity.vlan).one_or_none()
        if not vlan:
            raise VLANNotFoundError(str(entity.vlan))
        chambre.vlan_id = vlan.id

    chambre.updated_at = now
    return chambre

def _map_room_sql_to_abstract_entity(r: Chambre) -> AbstractRoom:
    from adh6.storage import db
    vlan = db.session.execute(select(Vlan).where(Vlan.id == r.vlan_id)).first()
    return AbstractRoom(
        id=r.id,
        room_number=r.numero,
        description=r.description,
        vlan=vlan[0].numero if vlan else None
    )


def _map_room_sql_to_entity(r: Chambre) -> Room:
    from adh6.storage import db
    vlan = db.session.execute(select(Vlan).where(Vlan.id == r.vlan_id)).first()
    return Room(
        id=r.id,
        room_number=r.numero,
        description=r.description,
        vlan=vlan[0].numero if vlan else None
    )
