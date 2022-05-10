# coding=utf-8
import abc
from typing import Optional
from src.entity import Port, AbstractPort
from src.use_case.interface.crud_repository import CRUDRepository


class PortRepository(CRUDRepository[Port, AbstractPort]):
    @abc.abstractmethod
    def get_rcom(self, ctx, id) -> Optional[int]:
        pass  # pragma: no cover
