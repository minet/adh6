# coding=utf-8
from src.entity import Device, AbstractDevice
from src.use_case.interface.crud_repository import CRUDRepository


class DeviceRepository(CRUDRepository[Device, AbstractDevice]):
    pass
