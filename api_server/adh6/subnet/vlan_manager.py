# coding=utf-8
from adh6.entity import Vlan
from adh6.exceptions import VLANNotFoundError
from adh6.default.crud_manager import CRUDManager
from adh6.decorator import log_call

from .interfaces import VlanRepository


class VlanManager(CRUDManager):
    def __init__(self, vlan_repository: VlanRepository):
        super().__init__(vlan_repository, VLANNotFoundError)
        self.vlan_repository = vlan_repository

    @log_call
    def get_from_number(self, ctx, vlan_number: int) -> Vlan:
        return self.vlan_repository.get_vlan(ctx, vlan_number)
