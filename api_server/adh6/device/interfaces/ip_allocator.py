# coding=utf-8
import abc
from typing import Union


class IpAllocator(abc.ABC):
    """
    Abstract interface to allocate IP addresses.
    """

    @abc.abstractmethod
    def available_ip(self, ctx, ip_range: str = "", member_id: Union[int, None] = None) -> str:
        """
        Allocates a new unused IP address.

        :raise NoMoreIPAvailable
        """
        pass  # pragma: no cover

