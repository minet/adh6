# coding=utf-8
from src.entity import AbstractPort
from src.exceptions import PortNotFoundError
from src.use_case.crud_manager import CRUDManager
from src.use_case.interface.port_repository import PortRepository
from src.use_case.decorator.security import SecurityDefinition, defines_security
from src.entity.roles import Roles

@defines_security(SecurityDefinition(
    item={
        "read": Roles.ADMIN,
        "update": Roles.ADMIN,
        "delete": Roles.ADMIN,
    },
    collection={
        "read": Roles.ADMIN,
        "create" : Roles.ADMIN,
    }
))

class PortManager(CRUDManager):
    def __init__(self, port_repository: PortRepository):
        super().__init__('port', port_repository, AbstractPort, PortNotFoundError)
        self.port_repository = port_repository
