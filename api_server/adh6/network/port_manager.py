# coding=utf-8
from adh6.entity import AbstractPort
from adh6.exceptions import PortNotFoundError
from adh6.default.crud_manager import CRUDManager
from adh6.network.interfaces.port_repository import PortRepository
from adh6.authentication.security import SecurityDefinition, defines_security, is_admin

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
