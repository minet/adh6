# coding=utf-8
import abc
from typing import List, Optional, Tuple, TypeVar, Generic, Union

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET

T = TypeVar('T')
AbstractT = TypeVar('AbstractT')

class CRUDRepository(abc.ABC, Generic[T, AbstractT]):
    @abc.abstractmethod
    def get_by_id(self, object_id: int) -> Union[T, None]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def search_by(self, limit: int = DEFAULT_LIMIT, offset: int = DEFAULT_OFFSET, terms: Optional[str] = None, filter_: Optional[AbstractT] = None) -> Tuple[List[T], int]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def create(self, object_to_create: AbstractT) -> T:
        pass  # pragma: no cover

    @abc.abstractmethod
    def update(self, object_to_update: AbstractT, override: bool = False) -> T:
        pass  # pragma: no cover

    @abc.abstractmethod
    def delete(self, object_id: int) -> T:
        pass  # pragma: no cover
