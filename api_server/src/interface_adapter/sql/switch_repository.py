# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.orm.session import Session

from src.constants import CTX_SQL_SESSION, DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity import AbstractSwitch, Switch
from src.exceptions import SwitchNotFoundError
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.sql.model.models import Switch as SQLSwitch
from src.use_case.interface.switch_repository import SwitchRepository


class SwitchSQLRepository(SwitchRepository):
    def get_community(self, ctx, switch_id: int) -> str:
        return super().get_community(ctx, switch_id)

    @log_call
    def get_by_id(self, ctx, object_id: int) -> AbstractSwitch:
        session: Session = ctx.get(CTX_SQL_SESSION)
        obj = session.query(SQLSwitch).filter(SQLSwitch.id == object_id).one_or_none()
        if obj is None:
            raise SwitchNotFoundError(object_id)
        return _map_switch_sql_to_abstract_entity(obj)

    @log_call
    def search_by(self, ctx, limit: int=DEFAULT_LIMIT, offset: int=DEFAULT_OFFSET, terms: Optional[str]=None, filter_: Optional[AbstractSwitch] = None) -> Tuple[List[AbstractSwitch], int]:
        session: Session = ctx.get(CTX_SQL_SESSION)

        query = session.query(SQLSwitch)


        if terms:
            query = query.filter(SQLSwitch.description.contains(terms) |
                         SQLSwitch.ip.contains(terms))
        if filter_:
            if filter_.id is not None:
                query = query.filter(SQLSwitch.id == filter_.id)
            if filter_.description:
                query = query.filter(SQLSwitch.description.contains(filter_.description))
            if filter_.ip is not None:
                query = query.filter(SQLSwitch.ip == filter_.ip)
            if filter_.community is not None:
                query = query.filter(SQLSwitch.communaute == filter_.community)


        count = query.count()
        query = query.order_by(SQLSwitch.created_at.asc())
        query = query.offset(offset)
        query = query.limit(limit)
        r = query.all()

        return list(map(lambda item: _map_switch_sql_to_abstract_entity(item), r)), count

    @log_call
    def create(self, ctx, abstract_switch: Switch) -> Switch:
        session: Session = ctx.get(CTX_SQL_SESSION)

        now = datetime.now()

        switch = SQLSwitch(
            ip=abstract_switch.ip,
            communaute=abstract_switch.community,
            description=abstract_switch.description,
            created_at=now,
            updated_at=now
        )

        session.add(switch)
        session.flush()

        return _map_switch_sql_to_entity(switch)

    @log_call
    def update(self, ctx, object_to_update: AbstractSwitch, override=False) -> object:
        session: Session = ctx.get(CTX_SQL_SESSION)

        query = session.query(SQLSwitch)
        query = query.filter(SQLSwitch.id == object_to_update.id)

        switch = query.one_or_none()
        if switch is None:
            raise SwitchNotFoundError(str(object_to_update.id))
        new_switch = _merge_sql_with_entity(object_to_update, switch, override)

        return _map_switch_sql_to_entity(new_switch)

    @log_call
    def delete(self, ctx, object_id) -> None:
        session: Session = ctx.get(CTX_SQL_SESSION)

        switch = session.query(SQLSwitch).filter(SQLSwitch.id == object_id).one_or_none()
        if switch is None:
            raise SwitchNotFoundError(object_id)

        session.delete(switch)
        session.flush()


def _merge_sql_with_entity(entity: AbstractSwitch, sql_object: SQLSwitch, override=False) -> SQLSwitch:
    now = datetime.now()
    switch = sql_object
    if entity.ip is not None or override:
        switch.ip = entity.ip
    if entity.community is not None or override:
        switch.communaute = entity.community
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
        description=a.description,
        ip=a.ip,
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
