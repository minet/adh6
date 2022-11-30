# coding=utf-8
import abc
import typing as t

from adh6.entity import AccountType

class AccountTypeRepository(abc.ABC):
    @abc.abstractmethod
    def get_by_id(self, object_id: int) -> AccountType:
        pass  # pragma: no cover

    @abc.abstractmethod
    def search_by(self, limit: int, offset: int, terms: t.Union[str, None] = None) -> t.Tuple[t.List[AccountType], int]:
        pass  # pragma: no cover
