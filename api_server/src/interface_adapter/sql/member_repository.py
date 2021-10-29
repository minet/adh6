# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from datetime import date, datetime, timezone
from typing import List, Tuple

from sqlalchemy.orm import Session

from src.constants import CTX_SQL_SESSION, DEFAULT_LIMIT, DEFAULT_OFFSET, MembershipStatus
from src.entity import AbstractMember, Room
from src.entity.member import Member
from src.entity.null import Null
from src.exceptions import InvalidMembershipDuration, RoomNotFoundError, MemberNotFoundError,\
    InvalidCharterID, CharterAlreadySigned, MembershipNotFoundError
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.sql.model.models import Adherent, Chambre, Membership as MembershipSQL
from src.interface_adapter.sql.room_repository import _map_room_sql_to_entity
from src.interface_adapter.sql.track_modifications import track_modifications
from src.use_case.interface.member_repository import MemberRepository


class MemberSQLRepository(MemberRepository):

    @log_call
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, filter_: AbstractMember = None) -> Tuple[List[Member], int]:
        session: Session = ctx.get(CTX_SQL_SESSION)
        query = session.query(Adherent)
        query = query.outerjoin(Chambre, Chambre.id == Adherent.chambre_id)

        if filter_.username is not None:
            query = query.filter(Adherent.login == filter_.username)

        if filter_.room is not None:
            if isinstance(filter_.room, Room):
                filter_.room = filter_.room.id
            query = query.filter(Adherent.chambre_id == filter_.room)

        if filter_.id is not None:
            query = query.filter(Adherent.id == filter_.id)

        if filter_.ip is not None:
            query = query.filter(Adherent.ip == filter_.ip)

        if terms:
            query = query.filter(
                (Adherent.nom.contains(terms)) |
                (Adherent.prenom.contains(terms)) |
                (Adherent.mail.contains(terms)) |
                (Adherent.login.contains(terms)) |
                (Adherent.commentaires.contains(terms))
            )

        count = query.count()
        query = query.order_by(Adherent.login.asc())
        query = query.offset(offset)
        query = query.limit(limit)
        r = query.all()

        return list(map(_map_member_sql_to_entity, r)), count

    @log_call
    def create(self, ctx, abstract_member: Member) -> object:
        session: Session = ctx.get(CTX_SQL_SESSION)

        now = datetime.now()

        room = None
        if abstract_member.room is not None:
            room = session.query(Chambre).filter(Chambre.id == abstract_member.room).one_or_none()
            if not room:
                raise RoomNotFoundError(abstract_member.room)

        member: Adherent = Adherent(
            nom=abstract_member.last_name,
            prenom=abstract_member.first_name,
            mail=abstract_member.email,
            login=abstract_member.username,
            chambre=room,
            created_at=now,
            updated_at=now,
            commentaires=abstract_member.comment,
            date_de_depart=abstract_member.departure_date or datetime.now().date(),
            mode_association=abstract_member.association_mode or datetime.now(),
        )

        with track_modifications(ctx, session, member):
            session.add(member)
        session.flush()

        return _map_member_sql_to_entity(member)

    def update(self, ctx, abstract_member: AbstractMember, override=False) -> object:
        session: Session = ctx.get(CTX_SQL_SESSION)

        query = session.query(Adherent)
        query = query.filter(Adherent.id == abstract_member.id)
        query = query.join(Chambre, Chambre.id == Adherent.chambre_id)

        adherent = query.one_or_none()
        if adherent is None:
            raise MemberNotFoundError(str(abstract_member.id))

        with track_modifications(ctx, session, adherent):
            new_adherent = _merge_sql_with_entity(ctx, abstract_member, adherent, override)

        return _map_member_sql_to_entity(new_adherent)

    @log_call
    def delete(self, ctx, member_id) -> None:
        session: Session = ctx.get(CTX_SQL_SESSION)

        member = session.query(Adherent).filter(Adherent.id == member_id).one_or_none()
        if member is None:
            raise MemberNotFoundError(member_id)

        with track_modifications(ctx, session, member):
            session.delete(member)

    @log_call
    def update_password(self, ctx, member_id, hashed_password):
        session: Session = ctx.get(CTX_SQL_SESSION)

        adherent = session.query(Adherent).filter(Adherent.id == member_id).one_or_none()

        if adherent is None:
            raise MemberNotFoundError(member_id)

        with track_modifications(ctx, session, adherent):
            adherent.password = hashed_password

    @log_call
    def update_charter(self, ctx, member_id: int, charter_id: int) -> None:
        session: Session = ctx.get(CTX_SQL_SESSION)

        query = session.query(Adherent)
        query = query.filter(Adherent.id == member_id)

        adherent = query.one_or_none()
        if adherent is None:
            raise MemberNotFoundError(str(member_id))

        membership: MembershipSQL = session.query(MembershipSQL) \
            .filter(MembershipSQL.adherent_id == member_id) \
            .filter(MembershipSQL.status == MembershipStatus.PENDING_RULES) \
            .one_or_none()

        if membership is None:
            raise MembershipNotFoundError(str(member_id))

        now = datetime.now()
        if charter_id == 1:
            if adherent.datesignedminet is not None or adherent.signedminet:
                raise CharterAlreadySigned("MiNET")
            with track_modifications(ctx, session, adherent):
                adherent.signedminet = True
                adherent.datesignedminet = now
            membership.status = MembershipStatus.PENDING_PAYMENT_INITIAL
        elif charter_id == 2:
            if adherent.datesignedhosting is not None or adherent.signedhosting:
                raise CharterAlreadySigned("Hosting")
            with track_modifications(ctx, session, adherent):
                adherent.signedhosting = True
                adherent.datesignedhosting = now
        else:
            raise InvalidCharterID(str(charter_id))
        session.flush()


    @log_call
    def get_charter(self, ctx, member_id: int, charter_id: int) -> str:
        session: Session = ctx.get(CTX_SQL_SESSION)

        query = session.query(Adherent)
        query = query.filter(Adherent.id == member_id)

        adherent: Adherent = query.one_or_none()
        if adherent is None:
            raise MemberNotFoundError(str(member_id))

        if charter_id == 1:
            return "" if adherent.signedminet is None else str(adherent.datesignedminet)
        if charter_id == 2:
            return "" if adherent.signedhosting is None else str(adherent.datesignedhosting)

        raise InvalidCharterID(str(charter_id))

    @log_call
    def add_duration(self, ctx, member_id: int, duration_in_mounth: int) -> None:
        now = date.today()
        session: Session = ctx.get(CTX_SQL_SESSION)
        query = session.query(Adherent).filter(Adherent.id == member_id)
        adherent: Adherent = query.one_or_none()
        if adherent is None:
            raise MemberNotFoundError(str(member_id))
        
        if duration_in_mounth not in [1, 2, 3, 4, 5, 12]:
            raise InvalidMembershipDuration(str(duration_in_mounth))
        
        if adherent.date_de_depart is None:
            adherent.date_de_depart = now
        
        if adherent.date_de_depart.month + duration_in_mounth > 12:
            adherent.date_de_depart = adherent.date_de_depart.replace(year=adherent.date_de_depart.year + 1, month=(adherent.date_de_depart.month + duration_in_mounth) - 12)
        else:
            adherent.date_de_depart = adherent.date_de_depart.replace(month=adherent.date_de_depart.month + duration_in_mounth)
        session.flush()


def _merge_sql_with_entity(ctx, entity: AbstractMember, sql_object: Adherent, override=False) -> Adherent:
    now = datetime.now()
    adherent = sql_object
    if entity.email is not None or override:
        adherent.mail = entity.email
    if entity.comment is not None or override:
        adherent.commentaires = entity.comment
    if entity.username is not None or override:
        adherent.login = entity.username
    if entity.first_name is not None or override:
        adherent.prenom = entity.first_name
    if entity.last_name is not None or override:
        adherent.nom = entity.last_name
    if entity.association_mode is not None or override:
        adherent.mode_association = entity.association_mode
    if entity.departure_date is not None or override:
        adherent.date_de_depart = entity.departure_date
    if entity.ip is not None or override:
        adherent.ip = entity.ip
    if entity.subnet is not None or override:
        adherent.subnet = entity.subnet
    if entity.room is not None:
        session: Session = ctx.get(CTX_SQL_SESSION)
        room = session.query(Chambre).filter(Chambre.id == entity.room).one_or_none()
        if not room:
            raise RoomNotFoundError(entity.room)
        adherent.chambre = room

    adherent.updated_at = now
    return adherent


def _map_member_sql_to_entity(adh: Adherent) -> Member:
    """
    Map a Adherent object from SQLAlchemy to a Member (from the entity folder/layer).
    """
    return Member(
        id=adh.id,
        username=adh.login,
        email=adh.mail,
        first_name=adh.prenom,
        last_name=adh.nom,
        departure_date=adh.date_de_depart,
        comment=adh.commentaires,
        association_mode=adh.mode_association.replace(tzinfo=timezone.utc) if adh.mode_association else None,
        ip=adh.ip,
        subnet=adh.subnet,
        room=_map_room_sql_to_entity(adh.chambre) if adh.chambre else Null(),
    )
