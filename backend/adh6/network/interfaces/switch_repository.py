import abc

from adh6.default.crud_repository import CRUDRepository
from adh6.entity import AbstractSwitch, Switch


class SwitchRepository(CRUDRepository[Switch, AbstractSwitch]):
    @abc.abstractmethod
    def get_community(self, switch_id: int) -> str:
        pass  # pragma: no cover
