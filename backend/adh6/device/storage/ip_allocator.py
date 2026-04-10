from ipaddress import AddressValueError, IPv4Network, ip_network

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.exceptions import BadSubnetError, NoMoreIPAvailableException

from ..interfaces import IpAllocator
from .models import Device


class IPSQLAllocator(IpAllocator):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def available_ip(self, ip_range: str = "", member_id: int | None = None) -> str:
        if ip_range == "":
            return "En attente"

        try:
            network = ip_network(ip_range)
        except AddressValueError:
            raise BadSubnetError("Unknown ip subnet")

        if isinstance(network, IPv4Network):
            smt = select(Device.ip).where(
                (Device.ip.is_not(None)) & (Device.ip != "En attente")
            )  # @TODO retrocompatibilité ADH5, à retirer à terme)
        else:
            smt = select(Device.ipv6).where(
                (Device.ipv6.is_not(None)) & (Device.ipv6 != "En attente")
            )  # @TODO retrocompatibilité ADH5, à retirer à terme)

        if member_id:
            smt = smt.where(Device.adherent_id == member_id)

        ips = (await self.session.execute(smt)).scalars().all()

        for index, host in enumerate(network.hosts()):
            if index == 0:
                continue
            if str(host) not in ips:
                return str(host)
        raise NoMoreIPAvailableException(ip_range)
