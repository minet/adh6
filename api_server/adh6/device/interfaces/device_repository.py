# coding=utf-8
import abc
from adh6.entity import Device, AbstractDevice
from adh6.default.crud_repository import CRUDRepository
from typing import Optional, Tuple, List


class DeviceRepository(CRUDRepository[Device, AbstractDevice]):
    @abc.abstractmethod
    def put_mab(self, ctx, id: int, mab: bool) -> bool:
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_mab(self, ctx, id: int) -> bool:
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_ip_address(self, ctx, type: str, filter_: Optional[AbstractDevice] = None) -> Tuple[List[str], int]:
        pass  # pragma: no cover
