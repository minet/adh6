# coding=utf-8
import json
from typing import List

from src.constants import DEFAULT_OFFSET, DEFAULT_LIMIT
from src.entity import Device, AbstractDevice
from src.exceptions import InvalidMACAddress, InvalidIPv4, InvalidIPv6
from src.exceptions import MemberNotFoundError, DeviceNotFoundError, IntMustBePositive
from src.use_case.interface.device_repository import DeviceRepository
from src.use_case.interface.ip_allocator import IPAllocator
from src.use_case.interface.member_repository import MemberRepository
from src.use_case.interface.room_repository import RoomRepository
from src.use_case.interface.vlan_repository import VLANRepository
from src.util.context import log_extra
from src.util.log import LOG
from src.util.validator import is_mac_address, is_ip_v4, is_ip_v6


class DeviceManager:
    def __init__(self,
                 member_repository: MemberRepository,
                 device_repository: DeviceRepository,
                 room_repository: RoomRepository,
                 vlan_repository: VLANRepository,
                 ip_allocator: IPAllocator):
        self.device_repository = device_repository
        self.member_repository = member_repository
        self.room_repository = room_repository
        self.vlan_repository = vlan_repository
        self.ip_allocator = ip_allocator

    def search(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, username=None, terms=None) -> (List[Device], int):
        """
        Search a device in the database.

        User story: As an admin, I can search all the devices, so I can see the device list of a member.

        :raise IntMustBePositiveException
        """
        if limit < 0:
            raise IntMustBePositive('limit')

        if offset < 0:
            raise IntMustBePositive('offset')

        result, count = self.device_repository.search_device_by(ctx, limit=limit, offset=offset, username=username,
                                                                terms=terms)

        LOG.info("device_search", extra=log_extra(
            ctx,
            limit=limit,
            terms=terms,
        ))

        return result, count

    def get_by_mac_address(self, ctx, mac_address: str) -> Device:
        """
        Get a device from the database.

        User story: As an admin, I can get a device, so I can see its information such as IP address.

        :raise DeviceNotFound
        """
        result, count = self.device_repository.search_device_by(ctx, mac_address=mac_address)
        if not result:
            raise DeviceNotFoundError(mac_address)

        LOG.info("device_get_by_username", extra=log_extra(
            ctx,
            mac_address=mac_address,
        ))

        return result[0]

    def delete(self, ctx, mac_address: str):
        """
        Delete a device from the database.

        User story: As an admin, I delete a device, so I can remove a device from a user profile.

        :raise DeviceNotFound
        """
        self.device_repository.delete_device(ctx, mac_address=mac_address)

        LOG.info("device_delete", extra=log_extra(
            ctx,
            mac=mac_address,
        ))

    def update_or_create(self, ctx, mac_address: str, dev: AbstractDevice):
        """
        Create/Update a device from the database.

        User story: As an admin, I can register a new device, so that a member can access internet with it.

        :return: True if the device was created, false otherwise.

        :raise MemberNotFound
        :raise IPAllocationFailedError
        :raise InvalidMACAddress
        :raise InvalidIPAddress
        """

        if not is_mac_address(dev.mac):
            raise InvalidMACAddress(dev.mac)

        # IP_V4_ADDRESS:
        if dev.ipv4_address is not None and not is_ip_v4(dev.ipv4_address):
            raise InvalidIPv4(dev.ipv4_address)

        # IP_V6_ADDRESS:
        if dev.ipv6_address is not None and not is_ip_v6(dev.ipv6_address):
            raise InvalidIPv6(dev.ipv6_address)

        # Make sure the provided owner username is valid.
        owner, _ = self.member_repository.search_member_by(ctx, member_id=dev.member)
        if not owner:
            raise MemberNotFoundError(dev.member)

        # Allocate IP address.
        ip_v4_range, ip_v6_range = self._get_ip_range_for_user(ctx, owner)

        # TODO: Free addresses if cannot allocate.
        if dev.ipv4_address is None and ip_v4_range:
            dev.ipv4_address = self.ip_allocator.allocate_ip_v4(ctx, ip_v4_range)

        if dev.ipv4_address is None and ip_v6_range:
            dev.ipv4_address = self.ip_allocator.allocate_ip_v6(ctx, ip_v6_range)

        fields = dev.to_dict()
        result, _ = self.device_repository.search_device_by(ctx, mac_address=mac_address)
        if not result:
            # No device with that MAC address, creating one...
            self.device_repository.create_device(ctx, **fields)

            LOG.info('device_create', extra=log_extra(
                ctx,
                username=owner.login,
                mac=mac_address,
                mutation=json.dumps(fields, sort_keys=True)
            ))
            return True

        else:
            # A device exists, updating it.

            # The following will never throw DeviceNotFound since we check beforehand.
            self.device_repository.update_device(ctx, mac_address, **fields)

            LOG.info('device_update', extra=log_extra(
                ctx,
                username=owner.login,
                mac=mac_address,
                mutation=json.dumps(fields, sort_keys=True)
            ))
            return False

    def _get_ip_range_for_user(self, ctx, username) -> (str, str):
        """
        Return the IP range that that a user should be assigned to.
        :return: IPv4 range and IPv6 range of the user
        """
        result, count = self.room_repository.search_room_by(ctx, owner_username=username)
        if not result:
            return None, None

        vlan = self.vlan_repository.get_vlan(ctx, result[0].vlan_number)
        return vlan.ipv4_network, vlan.ipv6_network
