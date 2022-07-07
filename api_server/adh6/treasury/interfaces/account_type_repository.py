# coding=utf-8
import abc
from typing import List, Optional, Tuple
from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity import AccountType

class AccountTypeRepository(abc.ABC):
    @abc.abstractmethod
    def get_by_id(self, ctx, object_id: int) -> AccountType:
        pass  # pragma: no cover

    @abc.abstractmethod
    def search_by(self, ctx, limit: int = DEFAULT_LIMIT, offset: int = DEFAULT_OFFSET, terms: Optional[str] = None) -> Tuple[List[AccountType], int]:
        pass  # pragma: no cover
    pass  # pragma: no cover
