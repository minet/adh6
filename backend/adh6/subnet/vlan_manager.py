from adh6.decorator import log_call
from adh6.entity import AbstractVlan, VlanStats

from .interfaces import VlanRepository


class VlanManager:
    def __init__(self, vlan_repository: VlanRepository):
        self.vlan_repository = vlan_repository

    @log_call
    async def get_from_number(self, vlan_number: int) -> AbstractVlan:
        return await self.vlan_repository.get_vlan(vlan_number)

    @log_call
    async def list_vlans(self) -> list[AbstractVlan]:
        return await self.vlan_repository.list_vlans()

    @log_call
    async def get_stats(self) -> list[VlanStats]:
        return await self.vlan_repository.get_stats()
