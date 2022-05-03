# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from datetime import datetime
from enum import Enum
from typing import List, Tuple

from sqlalchemy.orm.session import Session

from src.constants import CTX_SQL_SESSION, DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity import AbstractDevice, Member, AbstractMember
from src.entity.device import Device
from src.exceptions import DeviceNotFoundError, MemberNotFoundError
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.sql.model.models import Device as SQLDevice, Adherent
from src.interface_adapter.sql.track_modifications import track_modifications
from src.use_case.interface.device_repository import DeviceRepository


class DeviceType(Enum):
    wired = 0
    wireless = 1


class DeviceSQLRepository(DeviceRepository):

    def _search(self, session: Session, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None,
                filter_: AbstractDevice = None, query=None):
        query = query or session.query(SQLDevice)
        query = query.join(Adherent, Adherent.id == SQLDevice.adherent_id)

        if filter_ is not None:
            if filter_.id is not None:
                query = query.filter(SQLDevice.id == filter_.id)
            if filter_.member is not None:
                if isinstance(filter_.member, AbstractMember) or isinstance(filter_.member, Member):
                    query = query.filter(Adherent.id == filter_.member.id)
                else:
                    query = query.filter(Adherent.id == filter_.member)
            if filter_.mac:
                query = query.filter(SQLDevice.mac == filter_.mac)
            if filter_.connection_type:
                query = query.filter(SQLDevice.type == DeviceType[filter_.connection_type].value)

        if terms:
            query = query.filter(
                (SQLDevice.mac.contains(terms)) |
                (SQLDevice.mac.contains(terms.replace("-", ":"))) |
                (SQLDevice.ip.contains(terms)) |
                (SQLDevice.ipv6.contains(terms)) |
                (Adherent.login.contains(terms))
            )

        count = query.count()
        query = query.order_by(SQLDevice.created_at.asc())
        query = query.offset(offset)
        if limit > 0:
            query = query.limit(limit)
        r = query.all()

        return r, count

    @log_call
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None,
                  filter_: AbstractDevice = None) -> Tuple[List[Device], int]:
        session: Session = ctx.get(CTX_SQL_SESSION)
        r, count = self._search(session, limit, offset, terms, filter_)
        return list(map(_map_device_sql_to_entity, r)), count

    @log_call
    def create(self, ctx, abstract_device: Device) -> object:
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

    def get_ip_address(self, ctx, type: str, filter_: AbstractDevice = None) -> Tuple[List[str], int]:
        session: Session = ctx.get(CTX_SQL_SESSION)
        if type == "ipv4":
            query = session.query(SQLDevice.ip)
            query = query.filter((SQLDevice.ip != None) &
                         (SQLDevice.ip != "En attente")  # @TODO retrocompatibilité ADH5, à retirer à terme
                         )
        elif type == "ipv6":
            query = session.query(SQLDevice.ipv6)
            query = query.filter((SQLDevice.ipv6 != None) &
                         (SQLDevice.ipv6 != "En attente")  # @TODO retrocompatibilité ADH5, à retirer à terme
                         )
        r, count = self._search(session, limit=0, filter_=filter_, query=query)

        return list(map(lambda x: x[0], r)), count
    

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
