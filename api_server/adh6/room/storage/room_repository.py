"""
Implements everything related to actions on the SQL database.
"""

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import delete, insert, select, update

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.decorator import log_call
from adh6.entity import AbstractRoom, Room
from adh6.exceptions import RoomNotFoundError, VLANNotFoundError
from adh6.member.storage.models import Adherent
from adh6.storage import db
from adh6.subnet.storage.models import Vlan

from ..interfaces import RoomRepository
from .models import Chambre, RoomMemberLink


class RoomSQLRepository(RoomRepository):
    def get_from_member(self, member_id: int) -> Room | None:
        stmt = (
            select(Chambre)
            .join(RoomMemberLink, Chambre.id == RoomMemberLink.room_id)
            .where(RoomMemberLink.member_id == member_id)
        )

        with db.sessionmaker.begin() as session:
            result = session.execute(stmt).scalar_one_or_none()
            return _map_room_sql_to_entity(result, session) if result else None

    def get_members(self, room_id: int) -> Sequence[int]:
        stmt = select(RoomMemberLink.member_id).where(RoomMemberLink.room_id == room_id)

        with db.sessionmaker.begin() as session:
            return session.execute(stmt).scalars().all()

    def remove_member(self, member_id: int) -> None:
        stmt = delete(RoomMemberLink).where(RoomMemberLink.member_id == member_id)
        with db.sessionmaker.begin() as session:
            session.execute(stmt)

        # lines needed for compatibility
        with db.sessionmaker.begin() as session:
            adherent = session.query(Adherent).filter(Adherent.id == member_id).one()
            stmt = update(Adherent).where(Adherent.id == adherent.id).values(chambre_id=None)
            session.execute(stmt)

    def add_member(self, room_id: int, member_id: int) -> None:
        stmt = insert(RoomMemberLink).values(member_id=member_id, room_id=room_id)
        with db.sessionmaker.begin() as session:
            session.execute(stmt)

        # Those lines are needed for compatibility
        with db.sessionmaker.begin() as session:
            adherent = session.query(Adherent).filter(Adherent.id == member_id).one()
            stmt = update(Adherent).where(Adherent.id == adherent.id).values(chambre_id=room_id)
            session.execute(stmt)

    @log_call
    def get_by_id(self, object_id: int) -> AbstractRoom:
        with db.sessionmaker.begin() as session:
            obj = session.query(Chambre).filter(Chambre.id == object_id).one_or_none()
            if obj is None:
                raise RoomNotFoundError(object_id)
            return _map_room_sql_to_abstract_entity(obj, session)

    @log_call
    def search_by(
        self, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, filter_: AbstractRoom | None = None
    ) -> tuple[list[AbstractRoom], int]:
        with db.sessionmaker.begin() as session:
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

            return [_map_room_sql_to_abstract_entity(room, session) for room in r], count

    @log_call
    def create(self, abstract_room: Room) -> Room:
        with db.sessionmaker.begin() as session:
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

            session.add(room)
            session.flush()  # Ensure the room gets an ID
            # Map to entity while still in session context
            result = _map_room_sql_to_entity(room, session)

        return result

    @log_call
    def update(self, abstract_room: AbstractRoom, override=False) -> object:
        with db.sessionmaker.begin() as session:
            room = session.query(Chambre).filter(Chambre.id == abstract_room.id).one_or_none()
            if room is None:
                raise RoomNotFoundError(str(abstract_room.id))
            new_chambre = _merge_sql_with_entity(abstract_room, room, session, override)
            session.flush()
            mapped_room = _map_room_sql_to_entity(new_chambre, session)

        return mapped_room

    @log_call
    def delete(self, id) -> None:
        with db.sessionmaker.begin() as session:
            room = session.query(Chambre).filter(Chambre.id == id).one_or_none()
            if room is None:
                raise RoomNotFoundError(id)
            session.delete(room)


def _merge_sql_with_entity(entity: AbstractRoom, sql_object: Chambre, session, override=False) -> Chambre:
    now = datetime.now()
    chambre = sql_object
    if entity.description is not None or override:
        chambre.description = entity.description
    if entity.room_number is not None or override:
        chambre.numero = entity.room_number
    if entity.vlan is not None:
        vlan = session.query(Vlan).filter(Vlan.numero == entity.vlan).one_or_none()
        if not vlan:
            raise VLANNotFoundError(str(entity.vlan))
        chambre.vlan_id = vlan.id

    chambre.updated_at = now
    return chambre


def _map_room_sql_to_abstract_entity(r: Chambre, session=None) -> AbstractRoom:
    if session is not None:
        vlan = session.execute(select(Vlan).where(Vlan.id == r.vlan_id)).first()
    else:
        with db.sessionmaker.begin() as session:
            vlan = session.execute(select(Vlan).where(Vlan.id == r.vlan_id)).first()
    return AbstractRoom(id=r.id, room_number=r.numero, description=r.description, vlan=vlan[0].numero if vlan else None)


def _map_room_sql_to_entity(r: Chambre, session=None) -> Room:
    if session is not None:
        vlan = session.execute(select(Vlan).where(Vlan.id == r.vlan_id)).first()
    else:
        with db.sessionmaker.begin() as session:
            vlan = session.execute(select(Vlan).where(Vlan.id == r.vlan_id)).first()
    return Room(id=r.id, room_number=r.numero, description=r.description, vlan=vlan[0].numero if vlan else None)
