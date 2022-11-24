# coding=utf-8
import abc
import typing as t

from adh6.entity import Member, Device

class LogsRepository(abc.ABC):
    """
    Abstract interface to access the logs.
    """
    @abc.abstractmethod
    def get(self, member: Member, devices: t.List[Device], limit: int, dhcp: bool) -> t.List[t.Any]:
        """
        Get all the logs concerning the provided username and MAC addresses.
        """
        pass  # pragma: no cover

