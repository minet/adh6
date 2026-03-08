"""
Implements everything related to actions on the SQL database.
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import Select

from adh6.entity import AbstractDevice, Device, DeviceBody, DeviceFilter
from adh6.member.storage.models import Adherent
from adh6.storage.sql.models import Modification

from ..interfaces import DeviceRepository
from .models import Device as SQLDevice


class DeviceType(Enum):
    wired = 0
    wireless = 1


class DeviceSQLRepository(DeviceRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, object_id: int) -> Device | None:
        stmt = select(SQLDevice).where(SQLDevice.id == object_id)
        obj = await self.session.scalar(stmt)
        return _map_device_sql_to_entity(obj) if obj else None

    async def get_by_mac(self, mac: str) -> Device | None:
        stmt = select(SQLDevice).where(SQLDevice.mac == mac)
        obj = await self.session.scalar(stmt)
        return _map_device_sql_to_entity(obj) if obj else None

    async def search_by(
        self, limit: int, offset: int, device_filter: DeviceFilter
    ) -> tuple[list[Device], int]:
        stmt: Select = select(SQLDevice)
        if device_filter.terms:
            stmt = stmt.join(Adherent, SQLDevice.adherent_id == Adherent.id).where(
                (SQLDevice.mac.contains(device_filter.terms))
                | (SQLDevice.mac.contains(device_filter.terms.replace("-", ":")))
                | (SQLDevice.ip.contains(device_filter.terms))
                | (SQLDevice.ipv6.contains(device_filter.terms))
                | (Adherent.login.contains(device_filter.terms))
            )
        if device_filter.member:
            stmt = stmt.where(SQLDevice.adherent_id == device_filter.member)
        if device_filter.connection_type:
            stmt = stmt.where(
                SQLDevice.type == DeviceType[device_filter.connection_type].value
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        count = int((await self.session.execute(count_stmt)).scalar_one())

        rows = await self.session.scalars(stmt.offset(offset).limit(limit))
        devices = rows.all()

        return list(map(_map_device_sql_to_entity, devices)), count

    async def create(self, obj: DeviceBody) -> Device:
        now = datetime.now()
        device = SQLDevice(
            mac=obj.mac,
            created_at=now,
            updated_at=now,
            last_seen=now,
            type=DeviceType[obj.connection_type].value,  # type: ignore[index]  # TODO: typing is baaaaad
            adherent_id=obj.member,
            ip="En attente",
            ipv6="En attente",
        )
        self.session.add(device)
        await self.session.flush()
        await self._record_modification(
            adherent_id=device.adherent_id,
            action=f"device: created {device.mac}",
        )
        return _map_device_sql_to_entity(device)

    async def update(
        self, abstract_device: AbstractDevice, override: bool = False
    ) -> Device:
        stmt = select(SQLDevice).where(SQLDevice.id == abstract_device.id)
        device = await self.session.scalar(stmt)
        if device is None:
            raise ValueError(f"Device {abstract_device.id} not found")

        new_device = _merge_sql_with_entity(abstract_device, device, override)
        await self.session.flush()
        return _map_device_sql_to_entity(new_device)

    async def delete(self, object_id: int) -> None:
        stmt = select(SQLDevice).where(SQLDevice.id == object_id)
        device = await self.session.scalar(stmt)
        if device is None:
            return
        await self._record_modification(
            adherent_id=device.adherent_id,
            action=f"device: deleted {device.mac}",
        )
        await self.session.delete(device)

    async def get_mab(self, object_id: int) -> bool:
        stmt = select(SQLDevice).where(SQLDevice.id == object_id)
        device = await self.session.scalar(stmt)
        if device is None:
            raise ValueError(f"Device {object_id} not found")
        return device.mab

    async def put_mab(self, object_id: int, mab: bool) -> bool:
        stmt = select(SQLDevice).where(SQLDevice.id == object_id)
        device = await self.session.scalar(stmt)
        if device is None:
            raise ValueError(f"Device {object_id} not found")
        device.mab = mab
        return mab

    async def owner(self, id: int) -> int | None:
        stmt = select(SQLDevice.adherent_id).where(SQLDevice.id == id)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def set_name(self, id: int, name: str | None) -> None:
        stmt = select(SQLDevice).where(SQLDevice.id == id)
        device = await self.session.scalar(stmt)
        if device is None:
            raise ValueError(f"Device {id} not found")
        device.name = name
        device.updated_at = datetime.now()

    async def set_wifi_password(self, id: int, password: str | None) -> None:
        stmt = select(SQLDevice).where(SQLDevice.id == id)
        device = await self.session.scalar(stmt)
        if device is None:
            raise ValueError(f"Device {id} not found")
        device.wifi_password = password
        device.updated_at = datetime.now()

    async def _record_modification(self, adherent_id: int, action: str) -> None:
        now = datetime.now()
        self.session.add(
            Modification(
                adherent_id=adherent_id,
                action=action,
                created_at=now,
                updated_at=now,
                utilisateur_id=None,
            )
        )


def _merge_sql_with_entity(
    entity: AbstractDevice, sql_object: SQLDevice, override: bool = False
) -> SQLDevice:
    now = datetime.now()
    device = sql_object

    if entity.connection_type is not None or override:
        device.type = (
            DeviceType[entity.connection_type].value
            if entity.connection_type
            else device.type
        )
    if entity.mac is not None or override:
        device.mac = entity.mac
    if entity.member is not None or override:
        device.adherent_id = entity.member

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
        connectionType=DeviceType(d.type).name,
        ipv4Address=(
            d.ip if d.ip != "En attente" else None
        ),  # @TODO retrocompatibilite ADH5, a retirer a terme
        ipv6Address=(
            d.ipv6 if d.ipv6 != "En attente" else None
        ),  # @TODO retrocompatibilite ADH5, a retirer a terme
        name=d.name,
        wifiPassword=d.wifi_password,
        # @TODO 08/03/2026 liteapp: je vois toujours des entrées comme ça dans la db, donc il faudrait creuser pour voir d'où elles viennent
        # Je parierais sur Jenkins ou un bail comme ça
    )
