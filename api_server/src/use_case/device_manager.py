# coding=utf-8
from src.entity import AbstractDevice, Device
from src.exceptions import DeviceNotFoundError, InvalidMACAddress, InvalidIPv6, InvalidIPv4, DeviceAlreadyExists, DevicesLimitReached
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.use_case.crud_manager import CRUDManager
from src.use_case.decorator.auto_raise import auto_raise
from src.use_case.decorator.security import SecurityDefinition, defines_security, is_admin, owns, uses_security
from src.use_case.interface.device_repository import DeviceRepository
from src.use_case.interface.ip_allocator import IpAllocator
from src.util.validator import is_mac_address, is_ip_v4, is_ip_v6


@defines_security(SecurityDefinition(
    item={
        "read": owns(Device.member.id) | owns(AbstractDevice.member) | is_admin(),
        "update": owns(Device.member.id) | owns(Device.member) | owns(AbstractDevice.member) | is_admin(),
        "delete": owns(Device.member.id) | is_admin(),
        "admin": is_admin()
    },
    collection={
        "read": owns(AbstractDevice.member) | is_admin(),
        "create": owns(Device.member) | is_admin()
    }
))
class DeviceManager(CRUDManager):
    """
    Implements all the use cases related to device management.
    """

    def __init__(self,
                 device_repository: DeviceRepository,
                 ip_allocator: IpAllocator,
                 ):
        super().__init__('device', device_repository, AbstractDevice, DeviceNotFoundError)
        self.device_repository = device_repository
        self.ip_allocator = ip_allocator
        self.oui_repository = {}
        self.load_mac_oui_dict()

    def load_mac_oui_dict(self):
        with open('OUIs.txt', 'r', encoding='utf-8') as f:
            line = f.readline()
            while line != "":
                oui, company = line.split('\t')
                self.oui_repository[oui] = company
                line = f.readline()

    @log_call
    @auto_raise
    @uses_security("admin")
    def put_mab(self, ctx, device_id: int) -> bool:
        devices, _ = self.device_repository.search_by(ctx, filter_=AbstractDevice(id=device_id))
        if not devices:
            raise DeviceNotFoundError(str(device_id))
        
        mab = self.device_repository.get_mab(ctx, device_id)
        return self.device_repository.put_mab(ctx, device_id, not mab)

    @log_call
    @auto_raise
    @uses_security("admin")
    def get_mab(self, ctx, device_id: int) -> bool:
        devices, _ = self.device_repository.search_by(ctx, filter_=AbstractDevice(id=device_id))

        if not devices:
            raise DeviceNotFoundError(str(device_id))
        
        return self.device_repository.get_mab(ctx, device_id)


    @log_call
    @auto_raise
    def get_mac_vendor(self, ctx, device_id=None):
        devices, count = self.device_repository.search_by(ctx, filter_=AbstractDevice(id=device_id))

        if count == 0:
            raise DeviceNotFoundError(str(device_id))
        else:
            mac_address = devices[0].mac[:8].replace(":", "-")
            if mac_address not in self.oui_repository:
                vendor = "-"
            else:
                vendor = self.oui_repository[mac_address]

            return {"vendorname": vendor}


    @log_call
    @auto_raise
    def update_or_create(self, ctx, abstract_device: AbstractDevice, device_id=None):

        if abstract_device.mac is not None and not is_mac_address(abstract_device.mac):
            raise InvalidMACAddress(abstract_device.mac)
        if abstract_device.ipv4_address is not None and not is_ip_v4(abstract_device.ipv4_address):
            raise InvalidIPv4(abstract_device.ipv4_address)
        if abstract_device.ipv6_address is not None and not is_ip_v6(abstract_device.ipv6_address):
            raise InvalidIPv6(abstract_device.ipv6_address)

        result, count = self.device_repository.search_by(ctx, filter_=AbstractDevice(mac=abstract_device.mac))
        if count != 0 and device_id is None:
            raise DeviceAlreadyExists()
        elif count >= 20:
            raise DevicesLimitReached()
        else:
            device, created = super().update_or_create(ctx, abstract_device, device_id=device_id)

            if created:
                self.allocate_ip_addresses(ctx, device)

            return device, created

    @log_call
    @auto_raise
    def allocate_ip_addresses(self, ctx, device: Device, override: bool = False):
        from src.entity.validators.member_validators import is_member_active, has_member_subnet
        if is_member_active(device.member):
            if device.ipv4_address is None or override:
                if device.connection_type == "wired":
                    taken_ips, _ = self.device_repository.get_ip_address(ctx, 'ipv4', AbstractDevice(
                        connection_type=device.connection_type
                    ))

                    self.partially_update(ctx, AbstractDevice(
                        ipv4_address=self.ip_allocator.allocate_ip_v4(ctx, device.member.room.vlan.ipv4_network,
                                                                      taken_ips, should_skip_reserved=True)
                    ), device_id=device.id, override=False)
                elif device.connection_type == "wireless" and has_member_subnet(device.member):
                    taken_ips, _ = self.device_repository.get_ip_address(ctx, 'ipv4', AbstractDevice(
                        member=device.member,
                        connection_type=device.connection_type
                    ))

                    self.partially_update(ctx, AbstractDevice(
                        ipv4_address=self.ip_allocator.allocate_ip_v4(ctx, device.member.subnet, taken_ips)
                    ), device_id=device.id, override=False)
            if device.ipv6_address is None or override:
                if device.connection_type == "wired":
                    taken_ips, _ = self.device_repository.get_ip_address(ctx, 'ipv6', AbstractDevice(
                        connection_type=device.connection_type
                    ))

                    self.partially_update(ctx, AbstractDevice(
                        ipv6_address=self.ip_allocator.allocate_ip_v6(ctx, device.member.room.vlan.ipv6_network,
                                                                      taken_ips, should_skip_reserved=True)
                    ), device_id=device.id, override=False)

    @log_call
    @auto_raise
    def unallocate_ip_addresses(self, ctx, device: Device):
        from src.entity.validators.member_validators import is_member_active
        if not is_member_active(device.member):
            if device.ipv4_address is not None:
                self.partially_update(ctx, AbstractDevice(
                    ipv4_address='En attente'
                ), device_id=device.id, override=False)
            if device.ipv6_address is not None:
                self.partially_update(ctx, AbstractDevice(
                    ipv6_address='En attente'
                ), device_id=device.id, override=False)
