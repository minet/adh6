from adh6.decorator import log_call
from adh6.default.crud_manager import CRUDManager
from adh6.entity import Vlan
from adh6.exceptions import VLANNotFoundError

from .interfaces import VlanRepository


class VlanManager(CRUDManager):
    def __init__(self, vlan_repository: VlanRepository):
        super().__init__(vlan_repository, VLANNotFoundError)  # type: ignore # TODO: typing
        self.vlan_repository = vlan_repository

    @log_call
    async def get_from_number(self, vlan_number: int) -> Vlan:
        return await self.vlan_repository.get_vlan(vlan_number)
