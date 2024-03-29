# coding=utf-8

from adh6.exceptions import SwitchNotFoundError
from adh6.default.crud_manager import CRUDManager
from .interfaces.switch_repository import SwitchRepository


class SwitchManager(CRUDManager):
    """
    Implements all the use cases related to switch management.
    """

    def __init__(self, switch_repository: SwitchRepository):
        super().__init__(switch_repository, SwitchNotFoundError)
        self.switch_repository = switch_repository
