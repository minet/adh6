# coding=utf-8
from src.entity import AbstractPort
from src.exceptions import PortNotFoundError
from src.use_case.crud_manager import CRUDManager
from src.use_case.interface.port_repository import PortRepository


class PortManager(CRUDManager):
    def __init__(self, port_repository: PortRepository):
        super().__init__('port', port_repository, AbstractPort, PortNotFoundError)
        self.port_repository = port_repository
