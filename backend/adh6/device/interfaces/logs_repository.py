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
        self,
        member: Member,
        devices: list[Device] = [],
        limit: int = LOG_DEFAULT_LIMIT,
        offset: int = 0,
        dhcp: bool = False,
    ) -> tuple[list[t.Any], int]:
        """
        Get all the logs concerning the provided username and MAC addresses.

        Returns:
            tuple: (logs, total_count) where logs is the list of log entries
                  and total_count is the total number of available logs
        """
        # pragma: no cover
