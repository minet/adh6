from datetime import datetime
import uuid
import typing as t

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity import Membership, AbstractMembership, SubscriptionBody
from adh6.decorator import log_call
from adh6.storage import session

from .models import Membership as MembershipSQL
from .. import MembershipStatus
from ..interfaces import MembershipRepository


class MembershipSQLRepository(MembershipRepository):
    @log_call
    def search(self, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, filter_: t.Optional[AbstractMembership] = None) -> t.Tuple[t.List[Membership], int]:
        query = session.query(MembershipSQL)
        if filter_:
            if filter_.uuid is not None:
                query = query.filter(MembershipSQL.uuid == filter_.uuid)
            if filter_.status is not None:
                query = query.filter(MembershipSQL.status == filter_.status)
            if filter_.first_time is not None:
                query = query.filter(MembershipSQL.first_time == filter_.first_time)
            if filter_.duration is not None:
                query = query.filter(MembershipSQL.duration == filter_.duration)
            if filter_.payment_method is not None:
                query = query.filter(MembershipSQL.payment_method_id == filter_.payment_method)
            if filter_.account is not None:
                query = query.filter(MembershipSQL.account_id == filter_.account)
            if filter_.member is not None:
                query = query.filter(MembershipSQL.adherent_id == filter_.member)

        query = query.order_by(MembershipSQL.uuid)
        query = query.offset(offset)
        query = query.limit(limit)
        r = query.all()

        return list(map(_map_membership_sql_to_entity, r)), query.count()

    def create(self, body: SubscriptionBody, state: MembershipStatus) -> Membership:
        """
        Add a membership record.

        :raise MemberNotFound
        """
        now = datetime.now()
        to_add = MembershipSQL(
            uuid=str(uuid.uuid4()),
            duration=body.duration,
            account_id=body.account,
            payment_method_id=body.payment_method,
            adherent_id=body.member,
            status=state,
            create_at=now,
            update_at=now,
            first_time=session.query(MembershipSQL).filter(MembershipSQL.adherent_id == body.member).count() == 0,
            has_room=body.has_room if body.has_room is not None else True
        )
        session.add(to_add)
        session.flush()
        return _map_membership_sql_to_entity(to_add)

    def update(self, uuid: str, body: SubscriptionBody, state: MembershipStatus) -> Membership:
        now = datetime.now()
        query = session.query(MembershipSQL).filter(MembershipSQL.uuid == uuid)
        membership: MembershipSQL = query.one()

        if body.duration:
            membership.duration = body.duration
        if body.account:
            membership.account_id = body.account
        if body.payment_method:
            membership.payment_method_id = body.payment_method
        if body.has_room is not None:
            membership.has_room = body.has_room
        
        membership.status = state
        membership.update_at = now

        session.flush()
        return _map_membership_sql_to_entity(membership)

    def validate(self, uuid: str) -> None:
        query = session.query(MembershipSQL).filter(MembershipSQL.uuid == uuid)
        membership: MembershipSQL = query.one()
        membership.status = MembershipStatus.COMPLETE
        session.flush()


def _map_membership_sql_to_entity(obj_sql: MembershipSQL) -> Membership:
    """
    Map a Adherent object from SQLAlchemy to a Member (from the entity folder/layer).
    """
    return Membership(
        uuid=str(obj_sql.uuid),
        duration=obj_sql.duration,
        has_room=obj_sql.has_room,
        first_time=obj_sql.first_time,
        payment_method=obj_sql.payment_method_id,
        account=obj_sql.account_id,
        member=obj_sql.adherent_id,
        status=obj_sql.status.value,
        created_at=obj_sql.create_at
    )
