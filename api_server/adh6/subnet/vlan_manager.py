# coding=utf-8
from adh6.entity import AbstractVlan, Vlan
from adh6.exceptions import VLANNotFoundError
from adh6.default.crud_manager import CRUDManager
from adh6.subnet.interfaces.vlan_repository import VlanRepository
from adh6.authentication.security import SecurityDefinition, defines_security, is_admin, uses_security
from adh6.default.decorator.auto_raise import auto_raise
from adh6.default.decorator.log_call import log_call

@defines_security(SecurityDefinition(
    item={
        "read": is_admin(),
    }
))
class VlanManager(CRUDManager):
    def __init__(self, vlan_repository: VlanRepository):
        super().__init__(vlan_repository, AbstractVlan, VLANNotFoundError)
        self.vlan_repository = vlan_repository

    @log_call
    @auto_raise
    @uses_security("read", is_collection=False)
    def get_from_number(self, ctx, vlan_number: int) -> Vlan:
        return self.vlan_repository.get_vlan(ctx, vlan_number)
