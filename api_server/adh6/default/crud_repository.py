# coding=utf-8
import abc
import typing as t

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET

T = t.TypeVar('T')
AbstractT = t.TypeVar('AbstractT')

class CRUDRepository(abc.ABC, t.Generic[T, AbstractT]):
    @abc.abstractmethod
    def get_by_id(self, object_id: int) -> t.Union[T, None]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def search_by(self, limit: int = DEFAULT_LIMIT, offset: int = DEFAULT_OFFSET, terms: t.Optional[str] = None, filter_: t.Optional[AbstractT] = None) -> t.Tuple[t.List[T], int]:
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
