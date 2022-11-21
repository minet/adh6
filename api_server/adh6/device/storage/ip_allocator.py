# coding=utf-8
from ipaddress import AddressValueError, IPv4Network, ip_network
from typing import Union

from sqlalchemy import select

from adh6.storage import db
from adh6.exceptions import BadSubnetError, NoMoreIPAvailableException
from adh6.decorator import log_call

from ..interfaces import IpAllocator
from .models import Device


class IPSQLAllocator(IpAllocator):
    @log_call
    def available_ip(self, ip_range: str = "", member_id: Union[int, None] = None) -> str:
        if ip_range == "":
            return 'En attente'

        try:
            network = ip_network(ip_range)
        except AddressValueError:
            raise BadSubnetError("Unknown ip subnet")

        if isinstance(network, IPv4Network):
            smt = select(Device.ip).where((Device.ip != None) & (Device.ip != "En attente"))  # @TODO retrocompatibilité ADH5, à retirer à terme)
        else:
            smt = select(Device.ipv6).where((Device.ipv6 != None) & (Device.ipv6 != "En attente"))  # @TODO retrocompatibilité ADH5, à retirer à terme) 

        if member_id:
            smt = smt.where(Device.adherent_id == member_id)

        ips = db.session().execute(smt).scalars().all()
        for i, h in enumerate(network.hosts()):
            if i == 0:
                continue
            if str(h) not in ips:
                return str(h)
        raise NoMoreIPAvailableException(ip_range) 

