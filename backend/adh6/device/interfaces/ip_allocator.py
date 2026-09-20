import abc
from collections.abc import Collection


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
        excluded: Collection[str] = (),
    ) -> str:
        """
        Allocates a new unused IP address after the reserved first hosts, never one of `excluded`.

        :raise NoMoreIPAvailable
        """
        # pragma: no cover
