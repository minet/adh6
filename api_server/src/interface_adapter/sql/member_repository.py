# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
import uuid

from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session, Query
from sqlalchemy.sql.expression import desc, or_

from src.constants import CTX_SQL_SESSION, DEFAULT_LIMIT, DEFAULT_OFFSET, MembershipStatus
from src.entity import AbstractMember, Room, Membership, AbstractMembership, PaymentMethod, Account
from src.entity import member
from src.entity.member import Member
from src.entity.null import Null
from src.exceptions import RoomNotFoundError, MemberNotFoundError, MembershipAlreadyExist, MembershipPending, \
    InvalidCharterID, CharterAlreadySigned, MembershipNotFoundError, PaymentMethodNotFoundError, \
    MembershipStatusNotAllowed
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.sql.model.models import Adherent, Chambre
from src.interface_adapter.sql.model.models import Membership as MembershipSQL
from src.interface_adapter.sql.model.models import PaymentMethod as PaymentMethodSQL
from src.interface_adapter.sql.room_repository import _map_room_sql_to_entity
from src.interface_adapter.sql.account_type_repository import _map_account_type_sql_to_entity
from src.interface_adapter.sql.payment_method_repository import _map_payment_method_sql_to_entity
from src.interface_adapter.sql.track_modifications import track_modifications
from src.use_case.interface.member_repository import MemberRepository
from src.use_case.interface.membership_repository import MembershipRepository
from src.util.context import log_extra
from src.util.log import LOG


class MemberSQLRepository(MemberRepository, MembershipRepository):

    @log_call
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, filter_: AbstractMember = None) -> Tuple[List[Member], int]:
        s = ctx.get(CTX_SQL_SESSION)
        q = s.query(Adherent)
        q = q.outerjoin(Chambre, Chambre.id == Adherent.chambre_id)

        if filter_.username is not None:
            q = q.filter(Adherent.login == filter_.username)

        if filter_.room is not None:
            if isinstance(filter_.room, Room):
                filter_.room = filter_.room.id
            q = q.filter(Adherent.chambre_id == filter_.room)

        if filter_.id is not None:
            q = q.filter(Adherent.id == filter_.id)

        if filter_.ip is not None:
            q = q.filter(Adherent.ip == filter_.ip)

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

    @log_call
    def create(self, ctx, abstract_member: Member) -> object:
        s = ctx.get(CTX_SQL_SESSION)

        now = datetime.now()

        room = None
        if abstract_member.room is not None:
            room = s.query(Chambre).filter(Chambre.id == abstract_member.room).one_or_none()
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

        with track_modifications(ctx, s, member):
            s.add(member)
        s.flush()

        return _map_member_sql_to_entity(member)

    def update(self, ctx, abstract_member: AbstractMember, override=False) -> object:
        s = ctx.get(CTX_SQL_SESSION)

        q = s.query(Adherent)
        q = q.filter(Adherent.id == abstract_member.id)
        q = q.join(Chambre, Chambre.id == Adherent.chambre_id)

        adherent = q.one_or_none()
        if adherent is None:
            raise MemberNotFoundError(str(abstract_member.id))

        with track_modifications(ctx, s, adherent):
            new_adherent = _merge_sql_with_entity(ctx, abstract_member, adherent, override)

        return _map_member_sql_to_entity(new_adherent)

    @log_call
    def delete(self, ctx, member_id) -> None:
        s = ctx.get(CTX_SQL_SESSION)

        member = s.query(Adherent).filter(Adherent.id == member_id).one_or_none()
        if member is None:
            raise MemberNotFoundError(member_id)

        with track_modifications(ctx, s, member):
            s.delete(member)

    @log_call
    def update_password(self, ctx, member_id, hashed_password):
        s = ctx.get(CTX_SQL_SESSION)

        adherent = s.query(Adherent).filter(Adherent.id == member_id).one_or_none()

        if adherent is None:
            raise MemberNotFoundError(member_id)

        with track_modifications(ctx, s, adherent):
            adherent.password = hashed_password

    @log_call
    def update_charter(self, ctx, member_id: int, charter_id: int) -> None:
        s: Session = ctx.get(CTX_SQL_SESSION)

        q = s.query(Adherent)
        q = q.filter(Adherent.id == member_id)

        adherent = q.one_or_none()
        if adherent is None:
            raise MemberNotFoundError(str(member_id))

        membership: MembershipSQL = s.query(MembershipSQL) \
            .filter(MembershipSQL.adherent_id == member_id) \
            .filter(MembershipSQL.status == MembershipStatus.PENDING_RULES) \
            .one_or_none()

        if membership is None:
            raise MembershipNotFoundError(str(member_id))

        now = datetime.now()
        if charter_id == 1:
            if adherent.datesignedminet is not None or adherent.signedminet:
                raise CharterAlreadySigned("MiNET")
            with track_modifications(ctx, s, adherent):
                adherent.signedminet = True
                adherent.datesignedminet = now
            membership.status = MembershipStatus.PENDING_PAYMENT_INITIAL
        elif charter_id == 2:
            if adherent.datesignedhosting is not None or adherent.signedhosting:
                raise CharterAlreadySigned("Hosting")
            with track_modifications(ctx, s, adherent):
                adherent.signedhosting = True
                adherent.datesignedhosting = now
        else:
            raise InvalidCharterID(str(charter_id))
        s.flush()


    @log_call
    def get_charter(self, ctx, member_id: int, charter_id: int) -> str:
        s = ctx.get(CTX_SQL_SESSION)

        q = s.query(Adherent)
        q = q.filter(Adherent.id == member_id)

        adherent: Adherent = q.one_or_none()
        if adherent is None:
            raise MemberNotFoundError(str(member_id))

        if charter_id == 1:
            return "" if adherent.signedminet is None else str(adherent.datesignedminet)
        if charter_id == 2:
            return "" if adherent.signedhosting is None else str(adherent.datesignedhosting)

        raise InvalidCharterID(str(charter_id))

    @log_call
    def get_latest_membership(self, ctx, member_id: int) -> Membership:
        s: Session = ctx.get(CTX_SQL_SESSION)
        q = s.query(MembershipSQL).filter(MembershipSQL.adherent_id == member_id).filter(
                or_(
                    MembershipSQL.status == MembershipStatus.PENDING_RULES, 
                    MembershipSQL.status == MembershipStatus.PENDING_PAYMENT, 
                    MembershipSQL.status == MembershipStatus.PENDING_PAYMENT_INITIAL, 
                    MembershipSQL.status == MembershipStatus.PENDING_PAYMENT_VALIDATION
                )
            )
        membership: MembershipSQL = q.one_or_none()
        if membership is None:
            q = s.query(MembershipSQL).filter(MembershipSQL.adherent_id == member_id).filter(
                or_(
                    MembershipSQL.status == MembershipStatus.INITIAL,
                    MembershipSQL.status == MembershipStatus.COMPLETE,
                    MembershipSQL.status == MembershipStatus.ABORTED,
                    MembershipSQL.status == MembershipStatus.CANCELLED,
                )
            ).order_by(desc(MembershipSQL.create_at)).limit(1)
            membership = q.one_or_none()
            if membership is None:
                raise MembershipNotFoundError(str(member_id))
        
        return _map_membership_sql_to_entity(membership)

    @log_call
    def membership_search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None,
                             filter_: AbstractMembership = None) -> Tuple[List[Membership], int]:
        LOG.debug("sql_membership_repository_search_membership_called", extra=log_extra(ctx, filter_status=filter_.status))
        s = ctx.get(CTX_SQL_SESSION)
        q = s.query(MembershipSQL)
        q = q.outerjoin(Adherent, Adherent.id == MembershipSQL.adherent_id)
        q = q.outerjoin(Chambre, Chambre.id == Adherent.chambre_id)

        if filter_.uuid is not None:
            q = q.filter(MembershipSQL.uuid == filter_.uuid)
        if filter_.status is not None:
            LOG.debug(filter_.status)
            q = q.filter(MembershipSQL.status == filter_.status)
        if filter_.first_time is not None:
            q = q.filter(MembershipSQL.first_time == filter_.first_time)
        if filter_.duration is not None:
            q = q.filter(MembershipSQL.duration == filter_.duration)
        if filter_.payment_method is not None:
            if isinstance(filter_.payment_method, PaymentMethod):
                filter_.payment_method = filter_.payment_method.id
            q = q.filter(MembershipSQL.payment_method == filter_.payment_method)
        if filter_.account is not None:
            if isinstance(filter_.account, Account):
                filter_.account = filter_.account.id
            q = q.filter(MembershipSQL.account == filter_.account)
        if filter_.member is not None:
            if isinstance(filter_.member, Member):
                filter_.member = filter_.member.id
            q = q.filter(MembershipSQL.adherent_id == filter_.member)

        """
        if terms:
            q = q.filter(
                (Adherent.nom.contains(terms)) |
                (Adherent.prenom.contains(terms)) |
                (Adherent.mail.contains(terms)) |
                (Adherent.login.contains(terms)) |
                (Adherent.commentaires.contains(terms))
            )
        """

        q = q.order_by(MembershipSQL.uuid)
        q = q.offset(offset)
        q = q.limit(limit)
        r = q.all()

        return list(map(_map_membership_sql_to_entity, r)), q.count()

    @log_call
    def create_membership(self, ctx, member_id: int, membership: Membership) -> Membership:
        """
        Add a membership record.

        :raise MemberNotFound
        """
        now = datetime.now()
        s = ctx.get(CTX_SQL_SESSION)
        LOG.debug("sql_membership_repository_add_membership_called", extra=log_extra(ctx, member_id=member_id))

        # Check the member exists
        member: Adherent = s.query(Adherent).filter(Adherent.id == member_id).one_or_none()
        if member is None:
            raise MemberNotFoundError(str(member_id))

        # Check the transaction does not already exist
        _membership: Optional[MembershipSQL] = None
        if membership.uuid is not None:
            _membership = s.query(MembershipSQL).filter(MembershipSQL.uuid == membership.uuid).one_or_none()
        if _membership is not None:
            raise MembershipAlreadyExist()

        to_add: MembershipSQL = _map_entity_to_membership_sql(membership)
        to_add.uuid = str(uuid.uuid4())
        to_add.create_at = now
        to_add.update_at = now

        # Check any other membership from this member
        all_membership: List[MembershipSQL] = s.query(MembershipSQL) \
            .filter(MembershipSQL.adherent_id == member_id) \
            .all()

        # Check no other membership are Pending
        for i in all_membership:
            if i.status != MembershipStatus.COMPLETE or i.status != MembershipStatus.ABORTED or membership.status != MembershipStatus.CANCELLED:
                raise MembershipPending(i.uuid)

        to_add.first_time = len(all_membership) == 0
        s.add(to_add)
        s.flush()

        LOG.debug("sql_membership_repository_add_membership_finished", extra=log_extra(ctx, membership_uuid=to_add.uuid))

        return _map_membership_sql_to_entity(to_add)

    def update_membership(self, ctx, member_id: int, membership_uuid: str, abstract_membership: AbstractMembership) -> Membership:
        LOG.debug("sql_membership_repository_update_membership_called", extra=log_extra(ctx, membership_uuid=membership_uuid))
        now = datetime.now()
        s: Session = ctx.get(CTX_SQL_SESSION)
        adherent: Adherent = s.query(Adherent).filter(Adherent.id == member_id).one_or_none()
        if adherent is None:
            raise MemberNotFoundError(str(member_id))
        q: Query = s.query(MembershipSQL).filter(MembershipSQL.uuid == membership_uuid)
        membership: MembershipSQL = q.one_or_none()
        if membership is None:
            raise MembershipNotFoundError(membership_uuid)

        if abstract_membership.duration is not None:
            membership.duration = abstract_membership.duration
        if abstract_membership.products is not None:
            membership.products = str(abstract_membership.products)
        if abstract_membership.member is not None:
            if isinstance(abstract_membership.member, Member):
                abstract_membership.member = abstract_membership.member.id
            adherent: Adherent = s.query(Adherent).filter(Adherent.id == abstract_membership.member).one_or_none()
            if adherent is None:
                raise MemberNotFoundError(str(abstract_membership.member))
            membership.adherent = adherent
        if abstract_membership.payment_method is not None:
            if isinstance(abstract_membership.payment_method, PaymentMethod):
                abstract_membership.payment_method = abstract_membership.payment_method.id
            payment_method: PaymentMethod = s.query(PaymentMethodSQL).filter(PaymentMethodSQL.id == abstract_membership.payment_method).one_or_none()
            if payment_method is None:
                raise PaymentMethodNotFoundError(str(abstract_membership.payment_method))
            membership.payment_method = payment_method
        if abstract_membership.status is not None:
            membership.status = abstract_membership.status

        membership.update_at = now
        s.flush()

        LOG.debug("sql_membership_repository_update_membership_finished", extra=log_extra(ctx, duration=membership.duration))
        return _map_membership_sql_to_entity(q.one_or_none())

    def validate_membership(self, ctx, membership_uuid: str) -> None:
        s: Session = ctx.get(CTX_SQL_SESSION)
        q: Query = s.query(MembershipSQL).filter(MembershipSQL.uuid == membership_uuid)
        membership: MembershipSQL = q.one_or_none()
        if membership is None:
            raise MembershipNotFoundError(membership_uuid)
        if membership.status != MembershipStatus.PENDING_PAYMENT_VALIDATION:
            raise MembershipStatusNotAllowed(membership.status, "Should be PENDING_PAYMENT_VALIDATION")
        membership.status = MembershipStatus.COMPLETE
        s.flush()

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
        s = ctx.get(CTX_SQL_SESSION)
        room = s.query(Chambre).filter(Chambre.id == entity.room).one_or_none()
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


def _map_string_to_list(product_str: str) -> list:
    s = product_str.split(",")
    s[0] = s[0][1:]
    s[-1] = s[-1][:-1]
    return [int(elem) for elem in s]


def _map_membership_sql_to_entity(obj_sql: MembershipSQL) -> Membership:
    """
    Map a Adherent object from SQLAlchemy to a Member (from the entity folder/layer).
    """
    return Membership(
        uuid=str(obj_sql.uuid),
        duration=obj_sql.duration,
        products=_map_string_to_list(obj_sql.products),
        first_time=obj_sql.first_time,
        payment_method=_map_payment_method_sql_to_entity(obj_sql.payment_method) if obj_sql.payment_method else None,
        account=_map_account_type_sql_to_entity(obj_sql.account) if obj_sql.account else None,
        member=_map_member_sql_to_entity(obj_sql.adherent) if obj_sql.adherent else Null(),
        status=obj_sql.status if isinstance(obj_sql.status, str) else obj_sql.status.value,
    )


def _map_entity_to_membership_sql(entity: Membership) -> MembershipSQL:
    """
    Map a Adherent object from SQLAlchemy to a Member (from the entity folder/layer).
    """
    return MembershipSQL(
        uuid=entity.uuid,
        duration=entity.duration,
        products=str(entity.products),
        first_time=entity.first_time,
        payment_method_id=entity.payment_method,
        account_id=entity.account,
        adherent_id=entity.member,
        status=entity.status,
        create_at=entity.created_at,
        update_at=entity.updated_at
    )
