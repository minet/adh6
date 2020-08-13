# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""

import socket
import json

from datetime import datetime
from dateutil.parser import parse
from sqlalchemy.orm.exc import NoResultFound
from typing import List

from config import TEST_CONFIGURATION
from src.constants import CTX_SQL_SESSION, DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity import AbstractMember
from src.entity.member import Member
from src.entity.null import Null
from src.exceptions import RoomNotFoundError, MemberAlreadyExist, MemberNotFoundError
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.sql.model.models import Adherent, Chambre, Adhesion
from src.interface_adapter.sql.track_modifications import track_modifications
from src.use_case.interface.member_repository import MemberRepository
from src.use_case.interface.membership_repository import MembershipRepository
from src.util.context import log_extra
from src.util.date import date_to_string
from src.util.log import LOG


class MemberSQLRepository(MemberRepository, MembershipRepository):

    @log_call
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None,
                  filter_: AbstractMember = None) -> (List[Member], int):
        s = ctx.get(CTX_SQL_SESSION)
        q = s.query(Adherent)

        if filter_.username is not None:
            q = q.filter(Adherent.login == filter_.username)

        if filter_.room is not None:
            try:
                q2 = s.query(Chambre)
                q2 = q2.filter(Chambre.id == filter_.room)
                result = q2.one()
            except NoResultFound:
                return [], 0

            q = q.filter(Adherent.chambre == result)

        if filter_.id is not None:
            q = q.filter(Adherent.id == filter_.id)

        if terms:
            q = q.filter(
                (Adherent.nom.contains(terms)) |
                (Adherent.prenom.contains(terms)) |
                (Adherent.mail.contains(terms)) |
                (Adherent.login.contains(terms)) |
                (Adherent.commentaires.contains(terms))
            )

        count = q.count()
        q = q.order_by(Adherent.login.asc())
        q = q.offset(offset)
        q = q.limit(limit)
        r = q.all()

        return list(map(_map_member_sql_to_entity, r)), count

    def create(self, ctx, abstract_member: Member) -> object:
        s = ctx.get(CTX_SQL_SESSION)

        now = datetime.now()

        room = None
        if abstract_member.room is not None:
            room = s.query(Chambre).filter(Chambre.id == abstract_member.room).one_or_none()
            if not room:
                raise RoomNotFoundError(abstract_member.room)

        member = Adherent(
            nom=abstract_member.last_name,
            prenom=abstract_member.last_name,
            mail=abstract_member.email,
            login=abstract_member.username,
            chambre=room,
            created_at=now,
            updated_at=now,
            commentaires=abstract_member.comment,
            date_de_depart=abstract_member.departure_date.datetime.now().date(),
            mode_association=abstract_member.association_mode.datetime.now(),
        )

        with track_modifications(ctx, s, member):
            s.add(member)

        return _map_member_sql_to_entity(member)

    def update(self, ctx, abstract_member: AbstractMember, override=False) -> object:
        raise NotImplementedError

    @log_call
    def delete(self, ctx, member_id) -> None:
        s = ctx.get(CTX_SQL_SESSION)

        member = s.query(Adherent).filter(Adherent.id == member_id).one_or_none()
        if member is None:
            raise MemberNotFoundError(member_id)

        with track_modifications(ctx, s, member):
            s.delete(member)

    def create_membership(self, ctx, username, start: datetime, end: datetime) -> None:
        """
        Add a membership record.

        :raise MemberNotFound
        """
        s = ctx.get(CTX_SQL_SESSION)
        LOG.debug("sql_member_repository_add_membership_called", extra=log_extra(ctx, username=username))

        member = self.search_by(ctx, limit=1, filter_=AbstractMember(username=username))
        if member is None:
            raise MemberNotFoundError(username)

        s.add(Adhesion(
            adherent=member,
            depart=start,
            fin=end
        ))

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
        association_mode=adh.mode_association,
        room=adh.chambre.id if adh.chambre else Null(),
    )
