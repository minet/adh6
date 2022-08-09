# coding=utf-8
from adh6.exceptions import PortNotFoundError
from adh6.default.crud_manager import CRUDManager
from adh6.network.interfaces.port_repository import PortRepository


class PortManager(CRUDManager):
    def __init__(self, port_repository: PortRepository):
        super().__init__(port_repository, PortNotFoundError)
        self.port_repository = port_repository
