# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from datetime import datetime
from typing import List

from src.constants import CTX_SQL_SESSION, DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity import AbstractSwitch, Switch
from src.exceptions import SwitchNotFoundError
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.sql.model.models import Switch as SQLSwitch
from src.use_case.interface.switch_repository import SwitchRepository


class SwitchSQLRepository(SwitchRepository):

    @log_call
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None,
                  filter_: AbstractSwitch = None) -> (List[Switch], int):
        s = ctx.get(CTX_SQL_SESSION)

        q = s.query(SQLSwitch)


        if terms:
            q = q.filter(SQLSwitch.description.contains(terms) |
                         SQLSwitch.ip.contains(terms))
        if filter_:
            if filter_.id is not None:
                q = q.filter(SQLSwitch.id == filter_.id)
            if filter_.description:
                q = q.filter(SQLSwitch.description.contains(filter_.description))
            if filter_.ip is not None:
                q = q.filter(SQLSwitch.ip == filter_.ip)
            if filter_.community is not None:
                q = q.filter(SQLSwitch.communaute == filter_.community)


        count = q.count()
        q = q.order_by(SQLSwitch.created_at.asc())
        q = q.offset(offset)
        q = q.limit(limit)
        r = q.all()

        return list(map(lambda item: _map_switch_sql_to_entity(item), r)), count

    @log_call
    def create(self, ctx, abstract_switch: Switch) -> object:
        s = ctx.get(CTX_SQL_SESSION)

        now = datetime.now()

        switch = SQLSwitch(
            ip=abstract_switch.ip,
            communaute=abstract_switch.community,
            description=abstract_switch.description,
            created_at=now,
            updated_at=now
        )

        s.add(switch)
        s.flush()

        return _map_switch_sql_to_entity(switch)

    @log_call
    def update(self, ctx, object_to_update: AbstractSwitch, override=False) -> object:
        raise NotImplementedError

    @log_call
    def delete(self, ctx, object_id) -> None:
        s = ctx.get(CTX_SQL_SESSION)

        switch = s.query(SQLSwitch).filter(SQLSwitch.id == object_id).one_or_none()
        if switch is None:
            raise SwitchNotFoundError(object_id)

        s.delete(switch)
        s.flush()


def _map_switch_sql_to_entity(a: SQLSwitch) -> Switch:
    """
    Map a Switch object from SQLAlchemy to a Switch (from the entity folder/layer).
    """
    return Switch(
        id=a.id,
        description=a.description,
        ip=a.ip,
        community=a.communaute,
    )