# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from datetime import datetime
from typing import List, Optional, Tuple

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity import AbstractSwitch, Switch
from adh6.exceptions import SwitchNotFoundError
from adh6.decorator import log_call
from adh6.storage import session

from .models import Switch as SQLSwitch
from ..interfaces import SwitchRepository


class SwitchSQLRepository(SwitchRepository):
    def get_community(self, switch_id: int) -> str:
        obj = session.query(SQLSwitch.communaute).filter(SQLSwitch.id == switch_id).one_or_none()
        return obj[0]

    @log_call
    def get_by_id(self, object_id: int) -> AbstractSwitch:
        obj = session.query(SQLSwitch).filter(SQLSwitch.id == object_id).one_or_none()
        if obj is None:
            raise SwitchNotFoundError(object_id)
        return _map_switch_sql_to_abstract_entity(obj)

    @log_call
    def search_by(self, limit: int=DEFAULT_LIMIT, offset: int=DEFAULT_OFFSET, terms: Optional[str]=None, filter_: Optional[AbstractSwitch] = None) -> Tuple[List[AbstractSwitch], int]:
        query = session.query(SQLSwitch)
        if terms:
            query = query.filter(SQLSwitch.description.contains(terms) | SQLSwitch.ip.contains(terms))
        if filter_:
            if filter_.id:
                query = query.filter(SQLSwitch.id == filter_.id)
            if filter_.description:
                query = query.filter(SQLSwitch.description.contains(filter_.description))
            if filter_.ip is not None:
                query = query.filter(SQLSwitch.ip == filter_.ip)


        count = query.count()
        query = query.order_by(SQLSwitch.created_at.asc())
        query = query.offset(offset)
        query = query.limit(limit)
        r = query.all()

        return list(map(lambda item: _map_switch_sql_to_abstract_entity(item), r)), count

    @log_call
    def create(self, abstract_switch: Switch) -> Switch:
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
    def update(self, object_to_update: AbstractSwitch, override=False) -> object:
        query = session.query(SQLSwitch)
        query = query.filter(SQLSwitch.id == object_to_update.id)

        switch = query.one_or_none()
        if switch is None:
            raise SwitchNotFoundError(str(object_to_update.id))
        new_switch = _merge_sql_with_entity(object_to_update, switch, override)

        return _map_switch_sql_to_entity(new_switch)

    @log_call
    def delete(self, object_id) -> None:
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
