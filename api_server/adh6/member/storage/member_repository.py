# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from datetime import date, datetime, timedelta
import ipaddress
from typing import List, Optional, Tuple

from adh6.entity import AbstractMember, Member, MemberFilter
from adh6.decorator import log_call
from adh6.storage import session
from adh6.storage.sql.track_modifications import track_modifications

from .models import Adherent, Membership
from ..interfaces.member_repository import MemberRepository


class MemberSQLRepository(MemberRepository):
    @log_call
    def search_by(self, limit: int, offset: int, terms: Optional[str] = None, filter_: Optional[MemberFilter] = None) -> Tuple[List[Member], int]:
        query = session.query(Adherent)
        if filter_:
            if filter_.ip:
                query = query.filter(Adherent.ip == filter_.ip)
            if filter_.since:
                query = query.filter(Adherent.date_de_depart >= filter_.since)
            if filter_.until:
                query = query.filter(Adherent.date_de_depart <= filter_.until)
            if filter_.membership:
                query = query.join(Membership, Membership.adherent_id == Adherent.id).filter(Membership.status == filter_.membership)

        if terms:
            query = query.filter(
                (Adherent.nom.contains(terms)) |
                (Adherent.prenom.contains(terms)) |
                (Adherent.mail.contains(terms)) |
                (Adherent.login.contains(terms)) |
                (Adherent.commentaires.contains(terms)) |
                (Adherent.ip.contains(terms)) |
                (Adherent.subnet.contains(terms))
            )

        count = query.count()
        query = query.order_by(Adherent.login.asc())
        query = query.offset(offset)
        query = query.limit(limit)
        r = query.all()

        return list(map(_map_member_sql_to_entity, r)), count

    @log_call
    def get_by_id(self, object_id: int) -> Optional[AbstractMember]:
        adh = session.query(Adherent).filter(Adherent.id == object_id).one_or_none()
        return _map_member_sql_to_abstract_entity(adh) if adh else None

    def get_by_login(self, login: str) -> Optional[Member]:
        adh = session.query(Adherent).filter(Adherent.login == login).one_or_none()
        return _map_member_sql_to_entity(adh) if adh else None

    @log_call
    def create(self, object_to_create: Member) -> object:
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
        session.add(member)
        session.flush()

        return _map_member_sql_to_entity(member)

    def update(self, abstract_member: AbstractMember, override=False) -> object:
        query = session.query(Adherent)\
            .filter(Adherent.id == abstract_member.id)

        adherent = query.one()

        with track_modifications(session, adherent):
            new_adherent = _merge_sql_with_entity(abstract_member, adherent, override)
        session.flush()

        return _map_member_sql_to_entity(new_adherent)

    @log_call
    def delete(self, member_id) -> None:
        member = session.query(Adherent).filter(Adherent.id == member_id).one_or_none()
        with track_modifications(session, member):
            session.delete(member)

    @log_call
    def update_password(self, member_id, hashed_password):
        adherent = session.query(Adherent).filter(Adherent.id == member_id).one_or_none()
        with track_modifications(session, adherent):
            adherent.password = hashed_password

    @log_call
    def add_duration(self, member_id: int, duration_in_mounth: int) -> None:
        now = date.today()
        query = session.query(Adherent).filter(Adherent.id == member_id)
        adherent: Adherent = query.one()
        
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
    
    def used_wireless_public_ips(self) -> List[ipaddress.IPv4Address]:
        q = session.query(Adherent.ip).filter(Adherent.ip != None)
        r = q.all()
        return [ipaddress.IPv4Address(i[0]) for i in r if i[0] is not None]

    @log_call
    def update_comment(self, member_id: int, comment: str) -> None:
        adherent = session.query(Adherent).filter(Adherent.id == member_id).one_or_none()
        with track_modifications(session, adherent):
            adherent.commentaires= comment

def _merge_sql_with_entity(entity: AbstractMember, sql_object: Adherent, override=False) -> Adherent:
    now = datetime.now()
    adherent = sql_object
    if entity.email is not None or override:
        adherent.mail = entity.email
    if entity.username is not None or override:
        adherent.login = entity.username
    if entity.first_name is not None or override:
        adherent.prenom = entity.first_name
    if entity.last_name is not None or override:
        adherent.nom = entity.last_name
    if entity.ip is not None or override:
        adherent.ip = entity.ip if entity.ip != "" else None
    if entity.subnet is not None or override:
        adherent.subnet = entity.subnet if entity.subnet != "" else None
    if entity.comment is not None or override:
        adherent.commentaires = entity.comment

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
