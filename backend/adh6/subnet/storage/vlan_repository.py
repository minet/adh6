"""
Implements everything related to actions on the SQL database.
"""

import ipaddress

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.device.storage.device_repository import DeviceType
from adh6.device.storage.models import Device as DeviceSQL
from adh6.entity import AbstractDevice, AbstractVlan, VlanStats
from adh6.exceptions import VLANNotFoundError
from adh6.member.storage.models import Adherent as AdherentSQL
from adh6.room.storage.models import Chambre as ChambreSQL

from ..interfaces import VlanRepository
from .models import Vlan as VlanSQL


class VLANSQLRepository(VlanRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_vlan(self, vlan_number: int) -> AbstractVlan:
        """
        Get a VLAN.

        :raise VlanNotFound
        """
        stmt = select(VlanSQL).where(VlanSQL.numero == vlan_number)
        vlan = await self.session.scalar(stmt)
        if not vlan:
            raise VLANNotFoundError(vlan_number)
        return _map_vlan_sql_to_abstract_entity(vlan)

    async def list_vlans(self) -> list[AbstractVlan]:
        result = await self.session.scalars(select(VlanSQL).order_by(VlanSQL.numero))
        return [_map_vlan_sql_to_abstract_entity(v) for v in result]

    async def get_stats(self) -> list[VlanStats]:
        # Count devices WITH an IP per VLAN (= IPs in use)
        count_stmt = (
            select(VlanSQL, func.count(DeviceSQL.id).label("device_count"))
            .outerjoin(ChambreSQL, ChambreSQL.vlan_id == VlanSQL.id)
            .outerjoin(AdherentSQL, AdherentSQL.chambre_id == ChambreSQL.id)
            .outerjoin(
                DeviceSQL,
                and_(
                    DeviceSQL.adherent_id == AdherentSQL.id,
                    DeviceSQL.ip.isnot(None),
                    DeviceSQL.ip != "En attente",
                    DeviceSQL.type != DeviceType.wireless.value,  # Wireless devices are on a private IP
                ),
            )
            .group_by(VlanSQL.id)
            .order_by(VlanSQL.numero)
        )

        # Devices WITHOUT an IP per VLAN (= over-limit candidates)
        no_ip_stmt = (
            select(VlanSQL.id.label("vlan_id"), DeviceSQL)
            .join(ChambreSQL, ChambreSQL.vlan_id == VlanSQL.id)
            .join(AdherentSQL, AdherentSQL.chambre_id == ChambreSQL.id)
            .join(DeviceSQL, DeviceSQL.adherent_id == AdherentSQL.id)
            .where((DeviceSQL.ip.is_(None)) | (DeviceSQL.ip == "En attente"))
        )

        count_rows = (await self.session.execute(count_stmt)).all()
        no_ip_rows = (await self.session.execute(no_ip_stmt)).all()

        over_limit_by_vlan: dict[int, list[AbstractDevice]] = {}
        for vlan_id, device in no_ip_rows:
            over_limit_by_vlan.setdefault(vlan_id, []).append(_map_device_sql_to_abstract(device))

        result = []
        for vlan, device_count in count_rows:
            capacity = _compute_capacity(vlan.adresses)
            result.append(
                VlanStats(
                    id=vlan.id,
                    number=vlan.numero,
                    ipv4Network=vlan.adresses,
                    ipv6Network=vlan.adressesv6,
                    deviceCount=device_count,
                    capacity=capacity,
                    overLimitDevices=over_limit_by_vlan.get(vlan.id, []),
                )
            )
        return result


def _compute_capacity(cidr: str | None) -> int | None:
    if not cidr:
        return None
    try:
        network = ipaddress.ip_network(cidr, strict=False)
        return max(0, network.num_addresses - 2)
    except ValueError:
        return None


def _map_vlan_sql_to_abstract_entity(r: VlanSQL) -> AbstractVlan:
    return AbstractVlan(
        id=r.id,
        number=r.numero,
        ipv4Network=r.adresses,
        ipv6Network=r.adressesv6,
    )


def _map_device_sql_to_abstract(d: DeviceSQL) -> AbstractDevice:
    return AbstractDevice(
        id=d.id,
        mac=d.mac or "",
        name=d.name,
        ipv4Address=None,
        ipv6Address=None,
    )
