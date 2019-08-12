# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from datetime import datetime
from dateutil.parser import parse
from sqlalchemy.orm.exc import NoResultFound
from typing import List
from gfshare import split
from gnupg import GPG

from src.constants import CTX_SQL_SESSION, DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity.member import Member
from src.exceptions import RoomNotFoundError, MemberAlreadyExist, MemberNotFoundError
from src.interface_adapter.sql.model.models import Adherent, Chambre, Adhesion, KeyShare, BureauMembers
from src.interface_adapter.sql.track_modifications import track_modifications
from src.use_case.interface.member_repository import MemberRepository
from src.use_case.interface.membership_repository import MembershipRepository
from src.util.context import log_extra
from src.util.date import date_to_string
from src.util.log import LOG


class MemberSQLRepository(MemberRepository, MembershipRepository):
    """
    Represent the interface to the SQL database.
    """

    def create_membership(self, ctx, username, start: datetime, end: datetime) -> None:
        """
        Add a membership record.

        :raise MemberNotFound
        """
        s = ctx.get(CTX_SQL_SESSION)
        LOG.debug("sql_member_repository_add_membership_called", extra=log_extra(ctx, username=username))

        member = _get_member_by_login(s, username)
        if member is None:
            raise MemberNotFoundError(username)

        s.add(Adhesion(
            adherent=member,
            depart=start,
            fin=end
        ))

    def create_member(self, ctx,
                      last_name=None, first_name=None, email=None, username=None, comment=None,
                      room_number=None, departure_date=None, association_mode=None, keypair=None
                      ) -> None:
        """
        Create a member.

        :raise RoomNotFound
        """
        s = ctx.get(CTX_SQL_SESSION)
        LOG.debug("sql_member_repository_create_member_called", extra=log_extra(ctx, username=username))

        now = datetime.now()

        room = None
        if room_number is not None:
            room = s.query(Chambre).filter(Chambre.numero == room_number).one_or_none()
            if not room:
                raise RoomNotFoundError(room_number)

        member = s.query(Adherent).filter(Adherent.login == username).one_or_none()
        if member is not None:
            raise MemberAlreadyExist()

        member = Adherent(
            nom=last_name,
            prenom=first_name,
            mail=email,
            login=username,
            chambre=room,
            created_at=now,
            updated_at=now,
            commentaires=comment,
            date_de_depart=_parse_date_or_none(departure_date),
            mode_association=_parse_date_or_none(association_mode),
        )

        with track_modifications(ctx, s, member):
            s.add(member)

        member = _get_member_by_login(s, member.login)

        members = get_bureau_members(s)

        for share in sss(keypair['private'], threshold=3, sharecount=5, members=members):
            keyshare = KeyShare(share=share['enc_data'],
                                share_coeff=share['coeff'],
                                member_id=share['member_id'],       # membre du bureau
                                adh_id=member.id)                   # adhérent
            s.add(keyshare)

    def update_member(self, ctx, member_to_update,
                      last_name=None, first_name=None, email=None, username=None, comment=None,
                      room_number=None, departure_date: str=None, association_mode: str=None, password=None
                      ) -> None:
        """
        Update a member.

        :raise MemberNotFound
        """
        s = ctx.get(CTX_SQL_SESSION)
        LOG.debug("sql_member_repository_update_member_called", extra=log_extra(ctx, username=member_to_update))

        member = _get_member_by_login(s, member_to_update)
        if member is None:
            raise MemberNotFoundError(member_to_update)

        with track_modifications(ctx, s, member):
            member.nom = last_name or member.nom
            member.prenom = first_name or member.prenom
            member.mail = email or member.mail
            member.commentaires = comment or member.commentaires
            member.login = username or member.login

            if departure_date is not None:
                member.date_de_depart = _parse_date_or_none(departure_date)

            if association_mode is not None:
                member.mode_association = _parse_date_or_none(association_mode)

            if room_number is not None:
                member.chambre = s.query(Chambre).filter(Chambre.numero == room_number).one()

            member.updated_at = datetime.now()

        member.password = password or member.password  # Will not be tracked.

    def delete_member(self, ctx, username=None) -> None:
        """
        Delete a member.

        :raise MemberNotFound
        """
        s = ctx.get(CTX_SQL_SESSION)
        LOG.debug("sql_member_repository_delete_member_called", extra=log_extra(ctx, username=username))

        # Find the soon-to-be deleted user
        member = _get_member_by_login(s, username)
        if not member:
            raise MemberNotFoundError(username)

        with track_modifications(ctx, s, member):
            # Actually delete it
            s.delete(member)

    def search_member_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, room_number=None, terms=None,
                         username=None) -> (
            List[Member], int):
        """
        Search a member.
        """
        s = ctx.get(CTX_SQL_SESSION)
        LOG.debug("sql_member_repository_search_member_by_called", extra=log_extra(ctx))
        q = s.query(Adherent)

        if username:
            q = q.filter(Adherent.login == username)

        if room_number:
            try:
                q2 = s.query(Chambre)
                q2 = q2.filter(Chambre.numero == room_number)
                result = q2.one()
            except NoResultFound:
                return [], 0

            q = q.filter(Adherent.chambre == result)

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


def _map_member_sql_to_entity(adh: Adherent) -> Member:
    """
    Map a Adherent object from SQLAlchemy to a Member (from the entity folder/layer).
    """
    departure_date = date_to_string(adh.date_de_depart)
    association_mode = date_to_string(adh.mode_association)

    room_number = None
    if adh.chambre is not None:
        room_number = str(adh.chambre.numero)

    return Member(
        username=adh.login,
        email=adh.mail,
        first_name=adh.prenom,
        last_name=adh.nom,
        departure_date=departure_date,
        comment=adh.commentaires,
        association_mode=association_mode,
        room_number=room_number,
    )


def _get_member_by_login(s, login) -> Adherent:
    return s.query(Adherent).filter(Adherent.login == login).one_or_none()


def _parse_date_or_none(d: str):
    if d is None:
        return None

    return parse(d)


def sss(private_key, threshold, sharecount, members):
    shares = split(threshold, sharecount, private_key)
    gpg = GPG(gnupghome='/root/.gnupg')

    for member, share, share_coeff in zip(members, shares.values(), shares.keys()):
        LOG.debug(share)
        LOG.debug(member.fp)
        LOG.debug(gpg.search_keys(member.fp))
        LOG.debug(gpg.encrypt(share, member.fp, always_trust=True).data)
        yield {'member_id': member.id,
               'enc_data': gpg.encrypt(share, member.fp, always_trust=True).data.decode('utf-8'), 'coeff': share_coeff}


def get_bureau_members(s):
    return s.query(BureauMembers).all()
