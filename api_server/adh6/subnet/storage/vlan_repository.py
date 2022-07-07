# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from sqlalchemy.orm.session import Session

from adh6.entity import AbstractVlan
from adh6.util.context import log_extra
from adh6.util.log import LOG
from adh6.constants import CTX_SQL_SESSION
from adh6.exceptions import VLANNotFoundError
from adh6.default.decorator.log_call import log_call
from adh6.storage.sql.models import Vlan as VlanSQL
from adh6.subnet.interfaces.vlan_repository import VlanRepository


class VLANSQLRepository(VlanRepository):
    @log_call
    def get_vlan(self, ctx, vlan_number: int) -> AbstractVlan:
        """
        Get a VLAN.

        :raise VlanNotFound
        """
        LOG.debug("vlan_sql_repository_get_vlan", extra=log_extra(ctx, vlan_number=vlan_number))

        session: Session = ctx.get(CTX_SQL_SESSION)
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
