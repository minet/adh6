# coding=utf-8
import abc
import typing as t


class IpAllocator(abc.ABC):
    """
    Abstract interface to allocate IP addresses.
    """

    @abc.abstractmethod
    def available_ip(self, ip_range: str = "", member_id: t.Union[int, None] = None) -> str:
        """
        Allocates a new unused IP address.

        :raise NoMoreIPAvailable
        """
        pass  # pragma: no cover

