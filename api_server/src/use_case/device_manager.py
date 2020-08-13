# coding=utf-8

from src.entity import AbstractDevice
from src.exceptions import DeviceNotFoundError, InvalidMACAddress
from src.use_case.crud_manager import CRUDManager
from src.use_case.interface.device_repository import DeviceRepository
from src.util.validator import is_mac_address


class DeviceManager(CRUDManager):
    """
    Implements all the use cases related to device management.
    """

    def __init__(self,
                 device_repository: DeviceRepository,
                 ):
        super().__init__('device', device_repository, AbstractDevice, DeviceNotFoundError)
        self.device_repository = device_repository

    def update_or_create(self, ctx, abstract_device: AbstractDevice, device_id=None):

        if abstract_device.mac is not None and not is_mac_address(abstract_device.mac):
            raise InvalidMACAddress(abstract_device.mac)
        device, created = super().update_or_create(ctx, abstract_device, device_id=device_id)

        if created:
            pass  # TODO ALLOCATE IP ADDRESSES

        return device, created
