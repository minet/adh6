# coding=utf-8
from src.entity import AbstractVlan, Vlan
from src.exceptions import VLANNotFoundError
from src.use_case.crud_manager import CRUDManager
from src.use_case.interface.vlan_repository import VlanRepository
from src.use_case.decorator.security import SecurityDefinition, defines_security, uses_security
from src.entity.roles import Roles
from src.use_case.decorator.auto_raise import auto_raise
from src.interface_adapter.http_api.decorator.log_call import log_call

@defines_security(SecurityDefinition(
    item={
        "read": Roles.ADMIN,
    }
))
class VlanManager(CRUDManager):
    def __init__(self, vlan_repository: VlanRepository):
        super().__init__('vlan', vlan_repository, AbstractVlan, VLANNotFoundError)
        self.vlan_repository = vlan_repository

    @log_call
    @auto_raise
    @uses_security("read", is_collection=False)
    def get_from_number(self, ctx, vlan_number: int) -> Vlan:
        return self.vlan_repository.get_vlan(ctx, vlan_number)
