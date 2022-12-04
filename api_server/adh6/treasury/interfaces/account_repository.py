# coding=utf-8
import abc
import typing as t

from adh6.entity import Account, AbstractAccount
from adh6.default import CRUDRepository


class AccountRepository(CRUDRepository[Account, AbstractAccount]):
    @abc.abstractmethod
    def get_by_name(self, name: str) -> t.Union[Account, None]:
        """
        Add a membership.
        """
        pass  # pragma: no cover
