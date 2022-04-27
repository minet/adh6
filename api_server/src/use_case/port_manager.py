# coding=utf-8
from src.entity import AbstractPort
from src.exceptions import PortNotFoundError
from src.use_case.crud_manager import CRUDManager
from src.use_case.interface.port_repository import PortRepository
from src.use_case.decorator.security import SecurityDefinition, defines_security, is_admin

@defines_security(SecurityDefinition(
    item={
        "read": is_admin(),
        "update": is_admin(),
        "delete": is_admin(),
    },
    collection={
        "read": is_admin(),
        "create" : is_admin(),
    }
))

class PortManager(CRUDManager):
    def __init__(self, port_repository: PortRepository):
        super().__init__(port_repository, AbstractPort, PortNotFoundError)
        self.port_repository = port_repository
