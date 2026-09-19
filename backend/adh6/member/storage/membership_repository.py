import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET, MembershipDuration, MembershipStatus
from adh6.datetime_utils import utc_now_naive
from adh6.entity import AbstractMembership, Membership
from adh6.exceptions import MembershipNotFoundError
from adh6.member.interfaces.membership_repository import MembershipRepository
from adh6.storage.count import count_rows

from .models import Membership as MembershipSQL


class MembershipSQLRepository(MembershipRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, object_id: str) -> Membership | None:
        membership = await self.session.scalar(select(MembershipSQL).where(MembershipSQL.uuid == object_id))
        return _map_membership_sql_to_entity(membership) if membership else None

    async def search_by(
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
            if filter_.member is not None:
                stmt = stmt.where(MembershipSQL.adherent_id == filter_.member)

        count = await count_rows(self.session, stmt)

        # Apply ordering and pagination
        stmt = stmt.order_by(MembershipSQL.uuid).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        r = result.scalars().all()

        return list(map(_map_membership_sql_to_entity, r)), count

    async def create(self, object_to_create: AbstractMembership) -> Membership:
        """
        Add a membership record.

        :raise MemberNotFound
        """
        if object_to_create.member is None:
            raise ValueError("A membership must have a member")

        now = utc_now_naive()

        # Check if this is the first membership for the member
        count_stmt = (
            select(func.count()).select_from(MembershipSQL).where(MembershipSQL.adherent_id == object_to_create.member)
        )
        count_result = await self.session.execute(count_stmt)
        is_first_time = count_result.scalar() == 0

        to_add = MembershipSQL(
            uuid=str(uuid.uuid4()),
            duration=MembershipDuration(object_to_create.duration or MembershipDuration.NONE),
            payment_method_id=object_to_create.payment_method,
            adherent_id=object_to_create.member,
            status=MembershipStatus(object_to_create.status or MembershipStatus.INITIAL.value),
            create_at=now,
            update_at=now,
            first_time=is_first_time,
            has_room=object_to_create.has_room if object_to_create.has_room is not None else True,
        )
        self.session.add(to_add)
        await self.session.flush()  # Ensure the membership gets an ID
        # Map to entity while still in session context
        return _map_membership_sql_to_entity(to_add)

    async def update(self, object_to_update: AbstractMembership, override: bool = False) -> Membership:
        if object_to_update.uuid is None:
            raise MembershipNotFoundError(None)

        now = utc_now_naive()

        stmt = select(MembershipSQL).where(MembershipSQL.uuid == object_to_update.uuid)
        membership = await self.session.scalar(stmt)
        if membership is None:
            raise MembershipNotFoundError(object_to_update.uuid)

        fields = object_to_update.model_fields_set
        if "duration" in fields or override:
            membership.duration = MembershipDuration(object_to_update.duration or MembershipDuration.NONE)
        if "payment_method" in fields or override:
            membership.payment_method_id = object_to_update.payment_method
        if "has_room" in fields or override:
            membership.has_room = object_to_update.has_room if object_to_update.has_room is not None else True
        if "member" in fields and object_to_update.member is not None:
            membership.adherent_id = object_to_update.member
        if "first_time" in fields or override:
            membership.first_time = object_to_update.first_time or False
        if "status" in fields or override:
            membership.status = MembershipStatus(object_to_update.status or MembershipStatus.INITIAL.value)

        membership.update_at = now
        await self.session.flush()
        return _map_membership_sql_to_entity(membership)

    async def delete(self, object_id: str) -> Membership:
        stmt = select(MembershipSQL).where(MembershipSQL.uuid == object_id)
        membership = await self.session.scalar(stmt)
        if membership is None:
            raise MembershipNotFoundError(object_id)

        result = _map_membership_sql_to_entity(membership)
        await self.session.delete(membership)
        return result

    async def validate(self, uuid: str) -> None:
        stmt = select(MembershipSQL).where(MembershipSQL.uuid == uuid)
        membership = await self.session.scalar(stmt)
        if membership is None:
            raise MembershipNotFoundError(uuid)
        membership.status = MembershipStatus.COMPLETE
        membership.update_at = utc_now_naive()
        await self.session.flush()


def _map_membership_sql_to_entity(obj_sql: MembershipSQL) -> Membership:
    """
    Map a Adherent object from SQLAlchemy to a Member (from the entity folder/layer).
    """
    return Membership(
        uuid=str(obj_sql.uuid),
        duration=obj_sql.duration,
        hasRoom=obj_sql.has_room,
        firstTime=obj_sql.first_time,
        paymentMethod=obj_sql.payment_method_id,
        member=obj_sql.adherent_id,
        status=obj_sql.status.value,
        createdAt=obj_sql.create_at,
        updatedAt=obj_sql.update_at,
    )
