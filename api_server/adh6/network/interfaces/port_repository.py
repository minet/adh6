# coding=utf-8
import abc

from adh6.default.crud_repository import CRUDRepository
from adh6.entity import AbstractPort, Port


class PortRepository(CRUDRepository[Port, AbstractPort]):
    @abc.abstractmethod
    def get_rcom(self, id) -> int | None:
        pass  # pragma: no cover
