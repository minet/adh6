# coding=utf-8
from src.constants import CTX_ADMIN
from src.entity import AbstractDevice
from src.exceptions import DeviceNotFoundError, InvalidMACAddress, InvalidIPv6, InvalidIPv4
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.use_case.crud_manager import CRUDManager
from src.use_case.decorator.auto_raise import auto_raise
from src.use_case.interface.device_repository import DeviceRepository
from src.util.validator import is_mac_address, is_ip_v4, is_ip_v6


class DeviceManager(CRUDManager):
    """
    Implements all the use cases related to device management.
    """

    def __init__(self,
                 device_repository: DeviceRepository,
                 ):
        super().__init__('device', device_repository, AbstractDevice, DeviceNotFoundError)
        self.device_repository = device_repository

    @auto_raise
    def delete_access_control_function(self, ctx, f, args, kwargs):
        admin = ctx.get(CTX_ADMIN)
        if 'device_id' in kwargs:
            device, count = self.repository.search_by(ctx, filter_=AbstractDevice(id=kwargs['device_id']))
            if count >= 1:
                if device[0].member.id == admin.id:
                    return args, kwargs, True
        return args, kwargs, False

    def update_or_create(self, ctx, abstract_device: AbstractDevice, device_id=None):

        if abstract_device.mac is not None and not is_mac_address(abstract_device.mac):
            raise InvalidMACAddress(abstract_device.mac)
        if abstract_device.ipv4_address is not None and not is_ip_v4(abstract_device.ipv4_address):
            raise InvalidIPv4(abstract_device.ipv4_address)
        if abstract_device.ipv6_address is not None and not is_ip_v6(abstract_device.ipv6_address):
            raise InvalidIPv6(abstract_device.ipv6_address)
        device, created = super().update_or_create(ctx, abstract_device, device_id=device_id)

        if created:
            pass  # TODO ALLOCATE IP ADDRESSES

        return device, created
