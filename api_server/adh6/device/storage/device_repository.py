# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Tuple

from sqlalchemy.orm.session import Session
from sqlalchemy import select
from sqlalchemy.sql.selectable import Select

from adh6.constants import CTX_SQL_SESSION, DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity import AbstractDevice, Device
from adh6.exceptions import DeviceNotFoundError, MemberNotFoundError
from adh6.default.decorator.log_call import log_call
from adh6.storage.sql.models import Device as SQLDevice, Adherent
from adh6.storage.sql.track_modifications import track_modifications
from adh6.device.interfaces.device_repository import DeviceRepository


class DeviceType(Enum):
    wired = 0
    wireless = 1


class DeviceSQLRepository(DeviceRepository):
    def _filter(self, smt: Select, filter_: Optional[AbstractDevice] = None) -> Select:
        if filter_ is not None:
            if filter_.id is not None:
                smt = smt.where(SQLDevice.id == filter_.id)
            if filter_.member is not None:
                smt = smt.where(Adherent.id == filter_.member)
            if filter_.mac:
                smt = smt.where(SQLDevice.mac == filter_.mac)
            if filter_.connection_type:
                smt = smt.where(SQLDevice.type == DeviceType[filter_.connection_type].value)
        return smt

    @log_call
    def get_by_id(self, ctx, object_id: int) -> AbstractDevice:
        session: Session = ctx.get(CTX_SQL_SESSION)
        obj = session.query(SQLDevice).filter(SQLDevice.id == object_id).one_or_none()
        if obj is None:
            raise DeviceNotFoundError(object_id)
        return _map_device_sql_to_abstract_entity(obj)

    @log_call
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, filter_: Optional[AbstractDevice] = None) -> Tuple[List[AbstractDevice], int]:
        session: Session = ctx.get(CTX_SQL_SESSION)
        smt: Select = select(SQLDevice).join(SQLDevice.adherent)
        if terms:
            smt = smt.where(
                (SQLDevice.mac.contains(terms)) |
                (SQLDevice.mac.contains(terms.replace("-", ":"))) |
                (SQLDevice.ip.contains(terms)) |
                (SQLDevice.ipv6.contains(terms)) |
                (Adherent.login.contains(terms))
            )
        smt = self._filter(smt, filter_)

        count = len(session.execute(smt).all())
        r = session.scalars(smt.offset(offset).limit(limit))

        return list(map(_map_device_sql_to_abstract_entity, r)), count

    @log_call
    def create(self, ctx, abstract_device: AbstractDevice) -> Device:
        session: Session = ctx.get(CTX_SQL_SESSION)

        now = datetime.now()

        adherent = None
        if abstract_device.member is not None:
            adherent = session.query(Adherent).filter(Adherent.id == abstract_device.member).one_or_none()
            if not adherent:
                raise MemberNotFoundError(abstract_device.member)

        device = SQLDevice(
            mac=str(abstract_device.mac).upper().replace(':', '-'),
            created_at=now,
            updated_at=now,
            last_seen=now,
            type=DeviceType[abstract_device.connection_type].value,
            adherent=adherent,
            ip=abstract_device.ipv4_address,
            ipv6=abstract_device.ipv6_address
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
        query = query.join(Adherent, Adherent.id == SQLDevice.adherent_id)

        device = query.one_or_none()
        if device is None:
            raise DeviceNotFoundError(str(abstract_device.id))

        with track_modifications(ctx, session, device):
            new_device = _merge_sql_with_entity(ctx, abstract_device, device, override)

        return _map_device_sql_to_entity(new_device)

    @log_call
    def delete(self, ctx, id) -> None:
        session: Session = ctx.get(CTX_SQL_SESSION)

        device = session.query(SQLDevice).filter(SQLDevice.id == id).one_or_none()

        if device is None:
            raise DeviceNotFoundError(id)

        with track_modifications(ctx, session, device):
            session.delete(device)

    def get_ip_address(self, ctx, type: str, filter_: Optional[AbstractDevice] = None) -> Tuple[List[str], int]:
        if type != "ipv4" and type != "ipv6":
            raise ValueError("Type not found")

        session: Session = ctx.get(CTX_SQL_SESSION)
        if type == "ipv4":
            smt = select(SQLDevice.ip).where((SQLDevice.ip != None) & (SQLDevice.ip != "En attente"))  # @TODO retrocompatibilité ADH5, à retirer à terme)
        elif type == "ipv6":
            smt = select(SQLDevice.ipv6).where((SQLDevice.ipv6 != None) & (SQLDevice.ipv6 != "En attente"))  # @TODO retrocompatibilité ADH5, à retirer à terme) 

        smt = self._filter(smt, filter_)

        count = len(session.execute(smt).all())
        r = session.scalars(smt)
        return list(map(lambda x: x, r)), count
    

    def get_mab(self, ctx, id: int) -> bool:
        session: Session = ctx.get(CTX_SQL_SESSION)
        device: SQLDevice = session.query(SQLDevice).filter(SQLDevice.id == id).one_or_none()
        if not device:
            raise DeviceNotFoundError(str(id))
        return device.mab

    def put_mab(self, ctx, id: int, mab: bool) -> bool:
        session: Session = ctx.get(CTX_SQL_SESSION)
        device: SQLDevice = session.query(SQLDevice).filter(SQLDevice.id == id).one_or_none()
        if not device:
            raise DeviceNotFoundError(str(id))
        
        device.mab = mab

        return mab


def _merge_sql_with_entity(ctx, entity: AbstractDevice, sql_object: SQLDevice, override=False) -> SQLDevice:
    now = datetime.now()
    device = sql_object

    if entity.mac is not None or override:
        device.mac = entity.mac
    if entity.connection_type is not None:
        device.type = DeviceType[entity.connection_type].value
    if entity.ipv4_address is not None or override:
        device.ip = entity.ipv4_address
    if entity.ipv6_address is not None or override:
        device.ipv6 = entity.ipv6_address
    if entity.member is not None:
        session: Session = ctx.get(CTX_SQL_SESSION)
        adherent = session.query(Adherent).filter(Adherent.id == entity.member).one_or_none()
        if not adherent:
            raise MemberNotFoundError(entity.member)
        device.adherent = adherent
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

def _map_device_sql_to_abstract_entity(d: SQLDevice) -> AbstractDevice:
    """
    Map a Device object from SQLAlchemy to a Device (from the entity folder/layer).
    """
    return AbstractDevice(
        id=d.id,
        mac=d.mac,
        member=d.adherent_id,
        connection_type=DeviceType(d.type).name,
        ipv4_address=d.ip if d.ip != 'En attente' else None,  # @TODO retrocompatibilité ADH5, à retirer à terme
        ipv6_address=d.ipv6 if d.ipv6 != 'En attente' else None,  # @TODO retrocompatibilité ADH5, à retirer à terme
    )
