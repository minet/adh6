from datetime import datetime
import uuid
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import Session

from typing import List, Optional, Tuple
from adh6.entity.subscription_body import SubscriptionBody

from adh6.misc.log import LOG
from adh6.misc.context import log_extra
from adh6.constants import CTX_SQL_SESSION, DEFAULT_LIMIT, DEFAULT_OFFSET, MembershipStatus
from adh6.entity import Membership, AbstractMembership
from adh6.storage.sql.models import Membership as MembershipSQL
from adh6.default.decorator.log_call import log_call
from adh6.member.interfaces.membership_repository import MembershipRepository


class MembershipSQLRepository(MembershipRepository):
    @log_call
    def search(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, filter_: Optional[AbstractMembership] = None) -> Tuple[List[Membership], int]:
        LOG.debug("sql_membership_repository_search_membership_called", extra=log_extra(ctx))
        session: Session = ctx.get(CTX_SQL_SESSION)
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

    def create(self, ctx, body: SubscriptionBody, state: MembershipStatus) -> Membership:
        """
        Add a membership record.

        :raise MemberNotFound
        """
        now = datetime.now()
        session: Session = ctx.get(CTX_SQL_SESSION)
        LOG.debug("sql_membership_repository_add_membership_called", extra=log_extra(ctx))

        to_add = MembershipSQL(
            uuid=str(uuid.uuid4()),
            duration=body.duration,
            account_id=body.account,
            payment_method_id=body.payment_method,
            adherent_id=body.member,
            status=state,
            create_at=now,
            update_at=now,
            first_time=session.query(MembershipSQL).filter(MembershipSQL.adherent_id == body.member).count() == 0
        )

        session.add(to_add)
        session.flush()

        LOG.debug("sql_membership_repository_add_membership_finished", extra=log_extra(ctx, membership_uuid=to_add.uuid))

        return _map_membership_sql_to_entity(to_add)

    def update(self, ctx, uuid: str, body: SubscriptionBody, state: MembershipStatus) -> Membership:
        LOG.debug("sql_membership_repository_update_membership_called", extra=log_extra(ctx, uuid=uuid))
        now = datetime.now()
        session: Session = ctx.get(CTX_SQL_SESSION)
        query: Query = session.query(MembershipSQL).filter(MembershipSQL.uuid == uuid)
        membership: MembershipSQL = query.one()

        if body.duration:
            membership.duration = body.duration
        if body.account:
            membership.account_id = body.account
        if body.payment_method:
            membership.payment_method_id = body.payment_method
        
        membership.status = state
        membership.update_at = now

        session.flush()
        return _map_membership_sql_to_entity(membership)

    def validate(self, ctx, uuid: str) -> None:
        session: Session = ctx.get(CTX_SQL_SESSION)
        query: Query = session.query(MembershipSQL).filter(MembershipSQL.uuid == uuid)
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
        has_room=obj_sql.has_room is not None,
        first_time=obj_sql.first_time,
        payment_method=obj_sql.payment_method_id,
        account=obj_sql.account_id,
        member=obj_sql.adherent_id,
        status=obj_sql.status.value,
        created_at=obj_sql.create_at
    )
