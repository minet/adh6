# coding=utf-8
import abc
from typing import Optional
from adh6.entity import Port, AbstractPort
from adh6.default.crud_repository import CRUDRepository


class PortRepository(CRUDRepository[Port, AbstractPort]):
    @abc.abstractmethod
    def get_rcom(self, id) -> Optional[int]:
        pass  # pragma: no cover
