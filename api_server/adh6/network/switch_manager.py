# coding=utf-8

from adh6.entity import AbstractSwitch
from adh6.exceptions import SwitchNotFoundError
from adh6.default.crud_manager import CRUDManager
from adh6.network.interfaces.switch_repository import SwitchRepository
from adh6.authentication.security import SecurityDefinition, defines_security, is_admin

@defines_security(SecurityDefinition(
    item={
        "read": is_admin(),
        "update": is_admin(),
        "delete": is_admin()
    },
    collection={
        "read": is_admin(),
        "create" : is_admin(),
    }
))
class SwitchManager(CRUDManager):
    """
    Implements all the use cases related to switch management.
    """

    def __init__(self, switch_repository: SwitchRepository):
        super().__init__(switch_repository, AbstractSwitch, SwitchNotFoundError)
        self.switch_repository = switch_repository
