# coding=utf-8
import abc
from typing import List, Tuple, Union
from adh6.entity import Device, AbstractDevice, DeviceFilter, DeviceBody
from adh6.default.crud_repository import CRUDRepository


class DeviceRepository(CRUDRepository[Device, AbstractDevice]):
    @abc.abstractmethod
    def create(self, ctx, obj: DeviceBody) -> Device:
        pass  # pragma: no cover 

    @abc.abstractmethod
    def search_by(self, ctx, limit: int, offset: int, device_filter: DeviceFilter) -> Tuple[List[Device], int]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_by_mac(self, ctx, mac: str) -> Union[Device, None]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def put_mab(self, ctx, id: int, mab: bool) -> bool:
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_mab(self, ctx, id: int) -> bool:
        pass  # pragma: no cover

    @abc.abstractmethod
    def owner(self, ctx, id: int) -> Union[int, None]:
        pass  # pragma: no cover
