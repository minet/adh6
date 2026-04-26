from adh6.decorator import log_call
from adh6.default.crud_manager import CRUDManager
from adh6.entity import AbstractVlan, VlanStats
from adh6.exceptions import VLANNotFoundError

from .interfaces import VlanRepository


class VlanManager(CRUDManager):
    def __init__(self, vlan_repository: VlanRepository):
        super().__init__(vlan_repository, VLANNotFoundError)  # type: ignore # TODO: typing
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
