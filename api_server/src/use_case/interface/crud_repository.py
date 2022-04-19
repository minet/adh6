# coding=utf-8
import abc
from typing import List, Optional, Tuple, TypeVar, Generic

from src.constants import DEFAULT_LIMIT, DEFAULT_OFFSET

T = TypeVar('T')
AbstractT = TypeVar('AbstractT')

class CRUDRepository(abc.ABC, Generic[T, AbstractT]):
    @abc.abstractmethod
    def search_by(self, ctx, limit: int = DEFAULT_LIMIT, offset: int = DEFAULT_OFFSET, terms: Optional[str] = None, filter_: Optional[AbstractT] = None) -> Tuple[List[T], int]:
        pass

    @abc.abstractmethod
    def create(self, ctx, object_to_create: AbstractT) -> T:
        pass

    @abc.abstractmethod
    def update(self, ctx, object_to_update: AbstractT, override: bool = False) -> T:
        pass

    @abc.abstractmethod
    def delete(self, ctx, object_id: int) -> T:
        pass
