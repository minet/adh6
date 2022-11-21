# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from sqlalchemy.orm.session import Session

from adh6.entity import AbstractVlan
from adh6.exceptions import VLANNotFoundError
from adh6.decorator import log_call
from adh6.storage import session

from .models import Vlan as VlanSQL
from ..interfaces import VlanRepository


class VLANSQLRepository(VlanRepository):
    @log_call
    def get_vlan(self, vlan_number: int) -> AbstractVlan:
        """
        Get a VLAN.

        :raise VlanNotFound
        """
        vlan = session.query(VlanSQL).filter(VlanSQL.numero == vlan_number).one_or_none()
        if not vlan:
            raise VLANNotFoundError(vlan_number)
        return _map_vlan_sql_to_abstract_entity(vlan)


def _map_vlan_sql_to_abstract_entity(r: VlanSQL) -> AbstractVlan:
    return AbstractVlan(
        id=r.id,
        number=r.numero,
        ipv4_network=r.adresses,
        ipv6_network=r.adressesv6,
    )
