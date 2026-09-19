import abc


class IpAllocator(abc.ABC):
    """
    Abstract interface to allocate IP addresses.
    """

    @abc.abstractmethod
    async def available_ip(
        self,
        ip_range: str,
        member_id: int | None = None,
        reserved_hosts: int = 1,
    ) -> str:
        """
        Allocates a new unused IP address after the reserved first hosts.

        :raise NoMoreIPAvailable
        """
        # pragma: no cover
