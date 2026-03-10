import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET, MembershipStatus
from adh6.entity import AbstractMembership, Membership, SubscriptionBody

from ..interfaces.membership_repository import MembershipRepository
from .models import Membership as MembershipSQL


class MembershipSQLRepository(MembershipRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def search(
        self, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, filter_: AbstractMembership | None = None
    ) -> tuple[list[Membership], int]:
        stmt = select(MembershipSQL)

        if filter_:
            if filter_.uuid is not None:
                stmt = stmt.where(MembershipSQL.uuid == filter_.uuid)
            if filter_.status is not None:
                stmt = stmt.where(MembershipSQL.status == filter_.status)
            if filter_.first_time is not None:
                stmt = stmt.where(MembershipSQL.first_time == filter_.first_time)
            if filter_.duration is not None:
                stmt = stmt.where(MembershipSQL.duration == filter_.duration)
            if filter_.payment_method is not None:
                stmt = stmt.where(MembershipSQL.payment_method_id == filter_.payment_method)
            if filter_.account is not None:
                stmt = stmt.where(MembershipSQL.account_id == filter_.account)
            if filter_.member is not None:
                stmt = stmt.where(MembershipSQL.adherent_id == filter_.member)

        # Count
        count_result = await self.session.execute(stmt)
        count = len(count_result.all())

        # Apply ordering and pagination
        stmt = stmt.order_by(MembershipSQL.uuid).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        r = result.scalars().all()

        return list(map(_map_membership_sql_to_entity, r)), count

    async def create(self, body: SubscriptionBody, state: MembershipStatus) -> Membership:
        """
        Add a membership record.

        :raise MemberNotFound
        """
        now = datetime.now()

        # Check if this is the first membership for the member
        count_stmt = select(func.count()).select_from(MembershipSQL).where(MembershipSQL.adherent_id == body.member)
        count_result = await self.session.execute(count_stmt)
        is_first_time = count_result.scalar() == 0

        to_add = MembershipSQL(
            uuid=str(uuid.uuid4()),
            duration=body.duration,
            account_id=body.account,
            payment_method_id=body.payment_method,
            adherent_id=body.member,
            status=state,
            create_at=now,
            update_at=now,
            first_time=is_first_time,
            has_room=body.has_room if body.has_room is not None else True,
        )
        self.session.add(to_add)
        await self.session.flush()  # Ensure the membership gets an ID
        # Map to entity while still in session context
        result = _map_membership_sql_to_entity(to_add)
        return result

    async def update(self, uuid: str, body: SubscriptionBody, state: MembershipStatus) -> Membership:
        now = datetime.now()

        stmt = select(MembershipSQL).where(MembershipSQL.uuid == uuid)
        membership = await self.session.scalar(stmt)

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
        await self.session.flush()
        mapped_membership = _map_membership_sql_to_entity(membership)

        return mapped_membership

    async def validate(self, uuid: str) -> None:
        stmt = select(MembershipSQL).where(MembershipSQL.uuid == uuid)
        membership = await self.session.scalar(stmt)
        membership.status = MembershipStatus.COMPLETE


def _map_membership_sql_to_entity(obj_sql: MembershipSQL) -> Membership:
    """
    Map a Adherent object from SQLAlchemy to a Member (from the entity folder/layer).
    """
    return Membership(
        uuid=str(obj_sql.uuid),
        duration=obj_sql.duration,
        has_room=obj_sql.has_room,
        first_time=obj_sql.first_time,
        paymentMethod=obj_sql.payment_method_id,
        account=obj_sql.account_id,
        member=obj_sql.adherent_id,
        status=obj_sql.status.value,
        created_at=obj_sql.create_at,
    )
