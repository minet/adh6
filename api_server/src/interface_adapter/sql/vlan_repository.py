# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from sqlalchemy.orm.session import Session

from src.entity import Vlan
from src.entity.null import Null
from src.util.context import log_extra
from src.util.log import LOG
from src.constants import CTX_SQL_SESSION
from src.exceptions import VLANNotFoundError
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.sql.model.models import Vlan as VlanSQL
from src.use_case.interface.vlan_repository import VlanRepository


class VLANSQLRepository(VlanRepository):
    @log_call
    def get_vlan(self, ctx, vlan_number: int) -> Vlan:
        """
        Get a VLAN.

        :raise VlanNotFound
        """
        LOG.debug("vlan_sql_repository_get_vlan", extra=log_extra(ctx, vlan_number=vlan_number))

        session: Session = ctx.get(CTX_SQL_SESSION)
        vlan = session.query(VlanSQL).filter(VlanSQL.numero == vlan_number).one_or_none()
        if not vlan:
            raise VLANNotFoundError(vlan_number)
        print(vlan)
        return _map_vlan_sql_to_entity(vlan)


def _map_vlan_sql_to_entity(r: VlanSQL) -> Vlan:
    return Vlan(
        id=r.id,
        number=r.numero,
        ipv4_network=r.adresses or Null(),
        ipv6_network=r.adressesv6 or Null(),
    )