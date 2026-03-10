"""
Implements everything related to actions on the SQL database.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.entity import AbstractVlan
from adh6.exceptions import VLANNotFoundError

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


def _map_vlan_sql_to_abstract_entity(r: VlanSQL) -> AbstractVlan:
    return AbstractVlan(
        id=r.id,
        number=r.numero,
        ipv4Network=r.adresses,
        ipv6Network=r.adressesv6,
    )
