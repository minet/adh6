# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from datetime import date, datetime, timezone, timedelta
import ipaddress
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from src.constants import CTX_SQL_SESSION, DEFAULT_LIMIT, DEFAULT_OFFSET, MembershipStatus
from src.entity import AbstractMember
from src.entity.member import Member
from src.exceptions import InvalidMembershipDuration, RoomNotFoundError, MemberNotFoundError,\
    InvalidCharterID, CharterAlreadySigned, MembershipNotFoundError
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.sql.model.models import Adherent, Chambre, Membership as MembershipSQL
from src.interface_adapter.sql.track_modifications import track_modifications
from src.use_case.interface.member_repository import MemberRepository


class MemberSQLRepository(MemberRepository):

    @log_call
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms: Optional[str]=None, filter_: Optional[AbstractMember] = None) -> Tuple[List[AbstractMember], int]:
        session: Session = ctx.get(CTX_SQL_SESSION)
        query = session.query(Adherent)
        query = query.outerjoin(Chambre, Chambre.id == Adherent.chambre_id)

        if filter_ is not None:
            if filter_.username is not None:
                query = query.filter(Adherent.login == filter_.username)
            if filter_.room_number is not None:
                query = query.filter(Chambre.numero == filter_.room_number)
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

        return list(map(_map_member_sql_to_abstract_entity, r)), count

    @log_call
    def get_by_id(self, ctx, object_id: int) -> AbstractMember:
        session: Session = ctx.get(CTX_SQL_SESSION)
        adh = session.query(Adherent).filter(Adherent.id == object_id).one_or_none()
        if adh is None:
            raise MemberNotFoundError(object_id)
        return _map_member_sql_to_abstract_entity(adh)

    @log_call
    def create(self, ctx, abstract_member: Member) -> object:
        session: Session = ctx.get(CTX_SQL_SESSION)

        now = datetime.now()

        room = None
        if abstract_member.room_number is not None:
            room = session.query(Chambre).filter(Chambre.numero == abstract_member.room_number).one_or_none()
            if not room:
                raise RoomNotFoundError(abstract_member.room_number)

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

        query = session.query(Adherent)\
            .filter(Adherent.id == abstract_member.id)

        adherent = query.one_or_none()
        if adherent is None:
            raise MemberNotFoundError(str(abstract_member.id))

        with track_modifications(ctx, session, adherent):
            new_adherent = _merge_sql_with_entity(ctx, abstract_member, adherent, override)
        session.flush()

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
            if adherent.datesignedminet is not None:
                raise CharterAlreadySigned("MiNET")
            with track_modifications(ctx, session, adherent):
                adherent.datesignedminet = now
            membership.status = MembershipStatus.PENDING_PAYMENT_INITIAL
        elif charter_id == 2:
            if adherent.datesignedhosting is not None:
                raise CharterAlreadySigned("Hosting")
            with track_modifications(ctx, session, adherent):
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
            return "" if adherent.datesignedminet is None else str(adherent.datesignedminet)
        if charter_id == 2:
            return "" if adherent.datesignedhosting is None else str(adherent.datesignedhosting)

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
        
        if adherent.date_de_depart is None or adherent.date_de_depart < now:
            adherent.date_de_depart = now
        
        import calendar
        days_to_add = 0
        for i in range(duration_in_mounth):
            if adherent.date_de_depart.month+i <= 12:
                days_to_add += calendar.monthrange(adherent.date_de_depart.year, adherent.date_de_depart.month+i)[1]
            else:
                days_to_add += calendar.monthrange(adherent.date_de_depart.year + 1, adherent.date_de_depart.month + i - 12)[1]
        print(days_to_add)
        adherent.date_de_depart += timedelta(days=days_to_add)

        session.flush()
    
    def used_wireless_public_ips(self, ctx) -> List[ipaddress.IPv4Address]:
        session: Session = ctx.get(CTX_SQL_SESSION)
        q = session.query(Adherent.ip).filter(Adherent.ip is not None)
        r = q.all()
        return [ipaddress.IPv4Address(i[0]) for i in r if i[0] is not None]


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
        adherent.ip = entity.ip if entity.ip != "" else None
    if entity.subnet is not None or override:
        adherent.subnet = entity.subnet if entity.subnet != "" else None
    if entity.room_number is not None:
        if entity.room_number == -1:
            adherent.chambre_id = None
            adherent.chambre = None
        else:
            session: Session = ctx.get(CTX_SQL_SESSION)
            room = session.query(Chambre).filter(Chambre.numero == entity.room_number).one_or_none()
            if not room:
                raise RoomNotFoundError(entity.room_number)
            adherent.chambre = room

    adherent.updated_at = now
    return adherent

def _map_member_sql_to_abstract_entity(adh: Adherent) -> AbstractMember:
    """
    Map a Adherent object from SQLAlchemy to a Member (from the entity folder/layer).
    """
    return AbstractMember(
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
        room_number=adh.chambre.numero if adh.chambre else None,
    )

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
        room_number=adh.chambre.numero if adh.chambre else None,
    )
