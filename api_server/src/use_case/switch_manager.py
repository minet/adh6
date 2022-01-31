# coding=utf-8

from src.entity import AbstractSwitch
from src.exceptions import SwitchNotFoundError
from src.use_case.crud_manager import CRUDManager
from src.use_case.interface.switch_repository import SwitchRepository
from src.use_case.decorator.security import SecurityDefinition, defines_security
from src.entity.roles import Roles

@defines_security(SecurityDefinition(
    item={
        "read": Roles.ADMIN,
        "update": Roles.ADMIN,
    },
    collection={
        "read": Roles.ADMIN,
        "create" : Roles.ADMIN,
    }
))
class SwitchManager(CRUDManager):
    """
    Implements all the use cases related to switch management.
    """

    def __init__(self,
                 switch_repository: SwitchRepository,
                 ):
        super().__init__('switch', switch_repository, AbstractSwitch, SwitchNotFoundError)
        self.switch_repository = switch_repository