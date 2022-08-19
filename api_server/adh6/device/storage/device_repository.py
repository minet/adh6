# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from datetime import datetime
from enum import Enum
from typing import List, Tuple, Union

from sqlalchemy.orm.session import Session
from sqlalchemy import select
from sqlalchemy.sql.selectable import Select

from adh6.constants import CTX_SQL_SESSION
from adh6.entity import AbstractDevice, Device, DeviceFilter
from adh6.entity.device_body import DeviceBody
from adh6.default.decorator.log_call import log_call
from adh6.storage.sql.models import Device as SQLDevice, Adherent
from adh6.storage.sql.track_modifications import track_modifications
from adh6.device.interfaces.device_repository import DeviceRepository


class DeviceType(Enum):
    wired = 0
    wireless = 1


class DeviceSQLRepository(DeviceRepository):
    @log_call
    def get_by_id(self, ctx, object_id: int) -> Union[Device, None]:
        session: Session = ctx.get(CTX_SQL_SESSION)
        obj = session.query(SQLDevice).filter(SQLDevice.id == object_id).one_or_none()
        return _map_device_sql_to_entity(obj) if obj else None

    def get_by_mac(self, ctx, mac: str) -> Union[Device, None]:
        session: Session = ctx.get(CTX_SQL_SESSION)
        obj = session.query(SQLDevice).filter(SQLDevice.mac == mac).one_or_none()
        return _map_device_sql_to_entity(obj) if obj else None

    @log_call
    def search_by(self, ctx, limit: int, offset: int, device_filter: DeviceFilter) -> Tuple[List[Device], int]:
        session: Session = ctx.get(CTX_SQL_SESSION)
        smt: Select = select(SQLDevice)
        if device_filter.terms:
            smt = smt.join(Adherent, SQLDevice.adherent_id==Adherent.id).where(
                (SQLDevice.mac.contains(device_filter.terms)) |
                (SQLDevice.mac.contains(device_filter.terms.replace("-", ":"))) |
                (SQLDevice.ip.contains(device_filter.terms)) |
                (SQLDevice.ipv6.contains(device_filter.terms)) |
                (Adherent.login.contains(device_filter.terms))
            )
        if device_filter.member:
            smt = smt.where(SQLDevice.adherent_id == device_filter.member)
        if device_filter.connection_type:
            smt = smt.where(SQLDevice.type == DeviceType[device_filter.connection_type].value)

        count = len(session.execute(smt).all())
        r = session.scalars(smt.offset(offset).limit(limit))

        return list(map(_map_device_sql_to_entity, r)), count

    @log_call
    def create(self, ctx, obj: DeviceBody) -> Device:
        session: Session = ctx.get(CTX_SQL_SESSION)
        now = datetime.now()

        device = SQLDevice(
            mac=obj.mac,
            created_at=now,
            updated_at=now,
            last_seen=now,
            type=DeviceType[obj.connection_type].value,
            adherent_id=obj.member,
            ip='En attente',
            ipv6='En attente'
        )

        with track_modifications(ctx, session, device):
            session.add(device)
        session.flush()

        return _map_device_sql_to_entity(device)

    @log_call
    def update(self, ctx, abstract_device: AbstractDevice, override=False) -> Device:
        session: Session = ctx.get(CTX_SQL_SESSION)

        query = session.query(SQLDevice)
        query = query.filter(SQLDevice.id == abstract_device.id)

        device = query.one_or_none()
        with track_modifications(ctx, session, device):
            new_device = _merge_sql_with_entity(abstract_device, device, override)

        return _map_device_sql_to_entity(new_device)

    @log_call
    def delete(self, ctx, id) -> None:
        session: Session = ctx.get(CTX_SQL_SESSION)
        device = session.query(SQLDevice).filter(SQLDevice.id == id).one_or_none()
        with track_modifications(ctx, session, device):
            session.delete(device)    

    def get_mab(self, ctx, id: int) -> bool:
        session: Session = ctx.get(CTX_SQL_SESSION)
        device: SQLDevice = session.query(SQLDevice).filter(SQLDevice.id == id).one_or_none()
        return device.mab

    def put_mab(self, ctx, id: int, mab: bool) -> bool:
        session: Session = ctx.get(CTX_SQL_SESSION)
        device: SQLDevice = session.query(SQLDevice).filter(SQLDevice.id == id).one_or_none()
        device.mab = mab
        return mab

    def owner(self, ctx, id: int) -> Union[int, None]:
        session: Session = ctx.get(CTX_SQL_SESSION)
        smt = select(SQLDevice.adherent_id).where(SQLDevice.id == id)
        return session.execute(smt).scalar_one_or_none()


def _merge_sql_with_entity(entity: AbstractDevice, sql_object: SQLDevice, override=False) -> SQLDevice:
    now = datetime.now()
    device = sql_object

    if entity.ipv4_address is not None or override:
        device.ip = entity.ipv4_address
    if entity.ipv6_address is not None or override:
        device.ipv6 = entity.ipv6_address
    device.updated_at = now
    return device


def _map_device_sql_to_entity(d: SQLDevice) -> Device:
    """
    Map a Device object from SQLAlchemy to a Device (from the entity folder/layer).
    """
    return Device(
        id=d.id,
        mac=d.mac,
        member=d.adherent_id,
        connection_type=DeviceType(d.type).name,
        ipv4_address=d.ip if d.ip != 'En attente' else None,  # @TODO retrocompatibilité ADH5, à retirer à terme
        ipv6_address=d.ipv6 if d.ipv6 != 'En attente' else None,  # @TODO retrocompatibilité ADH5, à retirer à terme
    )
