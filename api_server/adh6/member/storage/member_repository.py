# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from datetime import date, datetime, timedelta
import ipaddress
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from adh6.constants import CTX_SQL_SESSION, MembershipStatus
from adh6.entity import AbstractMember
from adh6.entity.member import Member
from adh6.entity.member_filter import MemberFilter
from adh6.exceptions import InvalidMembershipDuration, MemberNotFoundError,\
    InvalidCharterID, CharterAlreadySigned, MembershipNotFoundError
from adh6.default.decorator.log_call import log_call
from adh6.storage.sql.models import Adherent, Membership as MembershipSQL
from adh6.storage.sql.track_modifications import track_modifications
from adh6.member.interfaces.member_repository import MemberRepository


class MemberSQLRepository(MemberRepository):
    @log_call
    def search_by(self, ctx, limit: int, offset: int, terms: Optional[str] = None, filter_: Optional[MemberFilter] = None) -> Tuple[List[Member], int]:
        session: Session = ctx.get(CTX_SQL_SESSION)
        query = session.query(Adherent)

        if filter_:
            if filter_.ip:
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
    def get_by_id(self, ctx, object_id: int) -> AbstractMember:
        session: Session = ctx.get(CTX_SQL_SESSION)
        adh = session.query(Adherent).filter(Adherent.id == object_id).one_or_none()
        if adh is None:
            raise MemberNotFoundError(object_id)
        return _map_member_sql_to_abstract_entity(adh)

    def get_by_login(self, ctx, login: str) -> Member:
        session: Session = ctx.get(CTX_SQL_SESSION)
        adh = session.query(Adherent).filter(Adherent.login == login).one_or_none()
        if adh is None:
            raise MemberNotFoundError(login)
        return _map_member_sql_to_entity(adh)

    @log_call
    def create(self, ctx, object_to_create: Member) -> object:
        session: Session = ctx.get(CTX_SQL_SESSION)

        now = datetime.now()

        member: Adherent = Adherent(
            nom=object_to_create.last_name,
            prenom=object_to_create.first_name,
            mail=object_to_create.email,
            login=object_to_create.username,
            created_at=now,
            updated_at=now,
            commentaires=object_to_create.comment,
            date_de_depart=object_to_create.departure_date,
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
            new_adherent = _merge_sql_with_entity(abstract_member, adherent, override)
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

        memberships: List[MembershipSQL] = session.query(MembershipSQL) \
            .filter(MembershipSQL.adherent_id == member_id) \
            .all()

        if not memberships:
            raise MembershipNotFoundError(str(member_id))

        now = datetime.now()
        if charter_id == 1:
            if adherent.datesignedminet is not None:
                raise CharterAlreadySigned("MiNET")
            with track_modifications(ctx, session, adherent):
                adherent.datesignedminet = now
            for m in memberships:
                if m.status == MembershipStatus.PENDING_RULES:
                    m.status = MembershipStatus.PENDING_PAYMENT_INITIAL
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
        adherent.date_de_depart += timedelta(days=days_to_add)

        session.flush()
    
    def used_wireless_public_ips(self, ctx) -> List[ipaddress.IPv4Address]:
        session: Session = ctx.get(CTX_SQL_SESSION)
        q = session.query(Adherent.ip).filter(Adherent.ip != None)
        r = q.all()
        return [ipaddress.IPv4Address(i[0]) for i in r if i[0] is not None]


def _merge_sql_with_entity(entity: AbstractMember, sql_object: Adherent, override=False) -> Adherent:
    now = datetime.now()
    adherent = sql_object
    if entity.mailinglist is not None or override:
        adherent.mailinglist = True
    if entity.mailinglist is not None or override:
        adherent.mail_membership = entity.mailinglist if entity.mailinglist else 0
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
    if entity.departure_date is not None or override:
        adherent.date_de_depart = entity.departure_date
    if entity.ip is not None or override:
        adherent.ip = entity.ip if entity.ip != "" else None
    if entity.subnet is not None or override:
        adherent.subnet = entity.subnet if entity.subnet != "" else None

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
        ip=adh.ip,
        subnet=adh.subnet,
        mailinglist=adh.mail_membership
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
        ip=adh.ip,
        subnet=adh.subnet,
        mailinglist=adh.mail_membership
    )
