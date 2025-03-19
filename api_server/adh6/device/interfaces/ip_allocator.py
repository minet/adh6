import abc


class IpAllocator(abc.ABC):
    """
    Abstract interface to allocate IP addresses.
    """

    @abc.abstractmethod
    def available_ip(self, ip_range: str = "", member_id: int | None = None) -> str:
        """
        Allocates a new unused IP address.

        :raise NoMoreIPAvailable
        """
        pass  # pragma: no cover
