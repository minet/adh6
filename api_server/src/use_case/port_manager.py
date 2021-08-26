# coding=utf-8
from src.entity import AbstractPort
from src.exceptions import PortNotFoundError
from src.use_case.crud_manager import CRUDManager
from src.use_case.interface.port_repository import PortRepository
from src.use_case.decorator.security import SecurityDefinition, defines_security
from src.entity.roles import Roles

@defines_security(SecurityDefinition(
    item={
        "read": Roles.ADH6_ADMIN,
        "update": Roles.ADH6_ADMIN,
    },
    collection={
        "read": Roles.ADH6_ADMIN,
        "create" : Roles.ADH6_ADMIN,
    }
))

class PortManager(CRUDManager):
    def __init__(self, port_repository: PortRepository):
        super().__init__('port', port_repository, AbstractPort, PortNotFoundError)
        self.port_repository = port_repository
