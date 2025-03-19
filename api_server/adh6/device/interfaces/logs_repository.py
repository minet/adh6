import abc
import typing as t

from adh6.constants import LOG_DEFAULT_LIMIT
from adh6.entity import Device, Member


class LogsRepository(abc.ABC):
    """
    Abstract interface to access the logs.
    """

    @abc.abstractmethod
    def get(
        self, member: Member, devices: list[Device] = [], limit: int = LOG_DEFAULT_LIMIT, dhcp: bool = False
    ) -> list[t.Any]:
        """
        Get all the logs concerning the provided username and MAC addresses.
        """
        pass  # pragma: no cover
