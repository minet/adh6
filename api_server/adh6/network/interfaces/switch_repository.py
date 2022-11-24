# coding=utf-8
import abc
from adh6.entity import Switch, AbstractSwitch
from adh6.default import CRUDRepository


class SwitchRepository(CRUDRepository[Switch, AbstractSwitch]):
    @abc.abstractmethod
    def get_community(self, switch_id: int) -> str:
        pass  # pragma: no cover
