# coding=utf-8
import abc
import typing as t
from adh6.entity import Device, AbstractDevice, DeviceFilter, DeviceBody, Member
from adh6.default.crud_repository import CRUDRepository


class DeviceRepository(CRUDRepository[Device, AbstractDevice]):
    @abc.abstractmethod
    def create(self, obj: DeviceBody, member: Member) -> Device:
        pass  # pragma: no cover 

    @abc.abstractmethod
    def search_by(self, limit: int, offset: int, device_filter: DeviceFilter) -> t.Tuple[t.List[Device], int]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_by_mac(self, mac: str) -> t.Union[Device, None]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def put_mab(self, id: int, mab: bool) -> bool:
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_mab(self, id: int) -> bool:
        pass  # pragma: no cover

    @abc.abstractmethod
    def owner(self, id: int) -> t.Union[int, None]:
        pass  # pragma: no cover
