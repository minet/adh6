# coding=utf-8
import abc
from src.entity import Device, AbstractDevice
from src.use_case.interface.crud_repository import CRUDRepository


class DeviceRepository(CRUDRepository[Device, AbstractDevice]):
    @abc.abstractmethod
    def put_mab(self, ctx, device_id: int, mab: bool) -> bool:
        pass

    @abc.abstractmethod
    def get_mab(self, ctx, device_id: int) -> bool:
        pass
    pass
