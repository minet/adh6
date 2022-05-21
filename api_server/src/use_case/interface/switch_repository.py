# coding=utf-8
import abc
from src.entity import Switch, AbstractSwitch
from src.use_case.interface.crud_repository import CRUDRepository


class SwitchRepository(CRUDRepository[Switch, AbstractSwitch]):
    @abc.abstractmethod
    def get_community(self, ctx, switch_id: int) -> str:
        pass  # pragma: no cover
