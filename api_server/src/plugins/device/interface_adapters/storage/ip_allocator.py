# coding=utf-8
from ipaddress import AddressValueError, IPv4Network, IPv6Network
from typing import List

from src.exceptions import BadSubnetError, NoMoreIPAvailableException
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.plugins.device.interfaces.ip_allocator import IpAllocator


class IPSQLAllocator(IpAllocator):

    @log_call
    def allocate_ip_v4(self, ctx, ip_range: str, taken_ips: List[str], should_skip_reserved=False) -> str:
        try:
            network = IPv4Network(ip_range)
        except AddressValueError as e:
            raise BadSubnetError("Unknown ipv4 subnet")

        i = 0
        for host in network.hosts():
            if i < 10 and (should_skip_reserved or i == 0):
                i += 1
                continue

            if str(host) not in taken_ips:
                return str(host)
        raise NoMoreIPAvailableException(ip_range)

    @log_call
    def allocate_ip_v6(self, ctx, ip_range: str, taken_ips: List[str], should_skip_reserved=False) -> str:
        try:
            network = IPv6Network(ip_range)
        except AddressValueError as e:
            raise BadSubnetError("Unknown ipv6 subnet")

        i = 0
        for host in network.hosts():
            if i < 10 and (should_skip_reserved or i == 0):
                i += 1
                continue

            if str(host) not in taken_ips:
                return str(host)
        raise NoMoreIPAvailableException(ip_range)


