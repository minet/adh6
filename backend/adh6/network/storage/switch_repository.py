"""
Implements everything related to actions on the SQL database.
"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity import AbstractSwitch, Switch
from adh6.exceptions import SwitchNotFoundError

from ..interfaces import SwitchRepository
from .models import Switch as SQLSwitch


class SwitchSQLRepository(SwitchRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_community(self, switch_id: int) -> str:
        result = await self.session.execute(select(SQLSwitch.communaute).where(SQLSwitch.id == switch_id))
        obj = result.scalar_one()
        return obj or ""

    async def get_by_id(self, object_id: int) -> Switch:
        stmt = select(SQLSwitch).where(SQLSwitch.id == object_id)
        obj = await self.session.scalar(stmt)
        if obj is None:
            raise SwitchNotFoundError(object_id)
        return _map_switch_sql_to_entity(obj)

    async def search_by(
        self,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        terms: str | None = None,
        filter_: AbstractSwitch | None = None,
    ) -> tuple[list[Switch], int]:
        stmt = select(SQLSwitch)

        if terms:
            stmt = stmt.where((SQLSwitch.description.contains(terms)) | (SQLSwitch.ip.contains(terms)))
        if filter_:
            if filter_.id:
                stmt = stmt.where(SQLSwitch.id == filter_.id)
            if filter_.description:
                stmt = stmt.where(SQLSwitch.description.contains(filter_.description))
            if filter_.ip is not None:
                stmt = stmt.where(SQLSwitch.ip == filter_.ip)

        # Count
        count_result = await self.session.execute(stmt)
        count = len(count_result.all())

        # Apply ordering and pagination
        stmt = stmt.order_by(SQLSwitch.created_at.asc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        r = result.scalars().all()

        return [_map_switch_sql_to_entity(item) for item in r], count

    async def create(self, abstract_switch: Switch) -> Switch:
        now = datetime.now()

        switch = SQLSwitch(
            ip=abstract_switch.ip,
            communaute=(abstract_switch.community.get_secret_value() if abstract_switch.community else None),
            description=abstract_switch.description,
            created_at=now,
            updated_at=now,
        )

        self.session.add(switch)
        await self.session.flush()  # Ensure the switch gets an ID
        # Map to entity while still in session context
        result = _map_switch_sql_to_entity(switch)

        return result

    async def update(self, object_to_update: AbstractSwitch, override=False) -> object:
        stmt = select(SQLSwitch).where(SQLSwitch.id == object_to_update.id)
        switch = await self.session.scalar(stmt)
        if switch is None:
            raise SwitchNotFoundError(str(object_to_update.id))
        new_switch = _merge_sql_with_entity(object_to_update, switch, override)
        await self.session.flush()
        mapped_switch = _map_switch_sql_to_entity(new_switch)

        return mapped_switch

    async def delete(self, object_id) -> None:
        stmt = select(SQLSwitch).where(SQLSwitch.id == object_id)
        switch = await self.session.scalar(stmt)
        if switch is None:
            raise SwitchNotFoundError(object_id)

        await self.session.delete(switch)


def _merge_sql_with_entity(entity: AbstractSwitch, sql_object: SQLSwitch, override=False) -> SQLSwitch:
    now = datetime.now()
    switch = sql_object
    if entity.ip is not None or override:
        switch.ip = entity.ip
    if entity.community is not None or override:
        switch.communaute = entity.community.get_secret_value() if entity.community else None
    if entity.description is not None:
        switch.description = entity.description

    switch.updated_at = now
    return switch


def _map_switch_sql_to_entity(a: SQLSwitch) -> Switch:
    """
    Map a Switch object from SQLAlchemy to a Switch (from the entity folder/layer).
    """
    return Switch(
        id=a.id,
        description=a.description or "",
        ip=a.ip or "",
    )


def _map_switch_sql_to_abstract_entity(a: SQLSwitch) -> AbstractSwitch:
    """
    Map a Switch object from SQLAlchemy to a Switch (from the entity folder/layer).
    """
    return AbstractSwitch(
        id=a.id,
        description=a.description,
        ip=a.ip,
    )
