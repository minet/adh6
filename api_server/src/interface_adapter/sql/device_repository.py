# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from datetime import datetime
from enum import Enum
from typing import List

from src.constants import CTX_SQL_SESSION, DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity import AbstractDevice, Member
from src.entity.device import Device
from src.entity.null import Null
from src.exceptions import DeviceNotFoundError, MemberNotFoundError
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.sql.member_repository import _map_member_sql_to_entity
from src.interface_adapter.sql.model.models import Device as SQLDevice, Adherent
from src.interface_adapter.sql.track_modifications import track_modifications
from src.use_case.interface.device_repository import DeviceRepository


class DeviceType(Enum):
    wired = 0
    wireless = 1


class DeviceSQLRepository(DeviceRepository):

    @log_call
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None,
                  filter_: AbstractDevice = None) -> (List[Device], int):
        s = ctx.get(CTX_SQL_SESSION)

        q = s.query(SQLDevice)
        q = q.join(Adherent, Adherent.id == SQLDevice.adherent_id)

        if filter_ is not None:
            if filter_.id is not None:
                q = q.filter(SQLDevice.id == filter_.id)
            if filter_.member is not None:
                if isinstance(filter_.member, Member):
                    q = q.filter(Adherent.id == filter_.member.id)
                else:
                    q = q.filter(Adherent.id == filter_.member)
            if filter_.mac:
                q = q.filter(SQLDevice.mac == filter_.mac)
            if filter_.connection_type:
                q = q.filter(SQLDevice.type == DeviceType[filter_.connection_type].value)

        if terms:
            q = q.filter(
                (SQLDevice.mac.contains(terms)) |
                (SQLDevice.mac.contains(terms.replace("-", ":"))) |
                (SQLDevice.ip.contains(terms)) |
                (SQLDevice.ipv6.contains(terms)) |
                (Adherent.login.contains(terms))
            )

        count = q.count()
        q = q.order_by(SQLDevice.created_at.asc())
        q = q.offset(offset)
        q = q.limit(limit)
        r = q.all()

        return list(map(_map_device_sql_to_entity, r)), count

    @log_call
    def create(self, ctx, abstract_device: Device) -> object:
        s = ctx.get(CTX_SQL_SESSION)

        now = datetime.now()

        adherent = None
        if abstract_device.member is not None:
            adherent = s.query(Adherent).filter(Adherent.id == abstract_device.member).one_or_none()
            if not adherent:
                raise MemberNotFoundError(abstract_device.member)

        device = SQLDevice(
            mac=abstract_device.mac,
            created_at=now,
            updated_at=now,
            last_seen=now,
            type=DeviceType[abstract_device.connection_type].value,
            adherent=adherent,
            ip=abstract_device.ipv4_address,
            ipv6=abstract_device.ipv6_address
        )

        with track_modifications(ctx, s, device):
            s.add(device)
        s.flush()

        return _map_device_sql_to_entity(device)

    @log_call
    def update(self, ctx, abstract_device: AbstractDevice, override=False) -> Device:
        s = ctx.get(CTX_SQL_SESSION)

        q = s.query(SQLDevice)
        q = q.filter(SQLDevice.id == abstract_device.id)
        q = q.join(Adherent, Adherent.id == SQLDevice.adherent_id)

        device = q.one_or_none()
        if device is None:
            raise DeviceNotFoundError(str(abstract_device.id))

        with track_modifications(ctx, s, device):
            new_device = _merge_sql_with_entity(ctx, abstract_device, device, override)

        return _map_device_sql_to_entity(new_device)

    @log_call
    def delete(self, ctx, device_id) -> None:
        s = ctx.get(CTX_SQL_SESSION)

        device = s.query(SQLDevice).filter(SQLDevice.id == device_id).one_or_none()

        if device is None:
            raise DeviceNotFoundError(device_id)

        with track_modifications(ctx, s, device):
            s.delete(device)


def _merge_sql_with_entity(ctx, entity: AbstractDevice, sql_object: SQLDevice, override=False) -> SQLDevice:
    now = datetime.now()
    device = sql_object
    if entity.mac is not None or override:
        device.mac = entity.mac
    if entity.connection_type is not None or override:
        device.type = DeviceType[entity.connection_type].value
    if entity.ipv4_address is not None or override:
        device.ip = entity.ipv4_address
    if entity.ipv6_address is not None or override:
        device.ipv6 = entity.ipv6_address
    if entity.member is not None:
        s = ctx.get(CTX_SQL_SESSION)
        adherent = s.query(Adherent).filter(Adherent.id == entity.member).one_or_none()
        if not adherent:
            raise MemberNotFoundError(entity.member)
        device.adherent = adherent

    device.updated_at = now
    return device


def _map_device_sql_to_entity(d) -> Device:
    """
    Map a Device object from SQLAlchemy to a Device (from the entity folder/layer).
    """
    return Device(
        id=d.id,
        mac=d.mac,
        member=_map_member_sql_to_entity(d.adherent),
        connection_type=DeviceType(d.type).name,
        ipv4_address=d.ip if d.ip != 'En attente' else Null(),  # @TODO retrocompatibilité ADH5, à retirer à terme
        ipv6_address=d.ipv6 if d.ipv6 != 'En attente' else Null(),  # @TODO retrocompatibilité ADH5, à retirer à terme
    )
