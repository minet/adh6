from ipaddress import IPv4Network, ip_network

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.device.interfaces import IpAllocator
from adh6.exceptions import BadSubnetError, NoMoreIPAvailableException

from .models import Device


class IPSQLAllocator(IpAllocator):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def available_ip(
        self,
        ip_range: str,
        member_id: int | None = None,
        reserved_hosts: int = 1,
    ) -> str:
        try:
            network = ip_network(ip_range)
        except ValueError as exc:
            raise BadSubnetError("Unknown ip subnet") from exc

        if isinstance(network, IPv4Network):
            smt = select(Device.ip).where(Device.ip.is_not(None))
        else:
            smt = select(Device.ipv6).where(Device.ipv6.is_not(None))

        if member_id:
            smt = smt.where(Device.adherent_id == member_id)

        ips = set((await self.session.execute(smt)).scalars().all())

        for index, host in enumerate(network.hosts()):
            if index < reserved_hosts:
                continue
            if str(host) not in ips:
                return str(host)
        raise NoMoreIPAvailableException(ip_range)
