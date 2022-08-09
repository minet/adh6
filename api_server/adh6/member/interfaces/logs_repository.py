# coding=utf-8
"""
Logs repository interface.
"""
import abc
from typing import Any, List, Optional

from adh6.entity import Device


class LogsRepository(abc.ABC):
    """
    Abstract interface to access the logs.
    """

    @abc.abstractmethod
    def get_global_stats(self, ctx):
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_logs(self, ctx, username: Optional[str] = None, devices: Optional[List[Device]] = None, dhcp: Optional[bool] = None) -> List[Any]:
        """
        Get all the logs concerning the provided username and MAC addresses.
        """
        pass  # pragma: no cover
