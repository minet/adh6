# coding=utf-8
"""
Logs repository interface.
"""
import abc


class LogsRepository(abc.ABC):
    """
    Abstract interface to access the logs.
    """

    @abc.abstractmethod
    def get_global_stats(self, ctx):
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_logs(self, ctx, username=None, devices=None, dhcp=None):
        """
        Get all the logs concerning the provided username and MAC addresses.
        """
        pass  # pragma: no cover
