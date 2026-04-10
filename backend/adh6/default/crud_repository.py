import abc
from typing import Generic, TypeVar

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET

T = TypeVar("T")
AbstractT = TypeVar("AbstractT")


class CRUDRepository(abc.ABC, Generic[T, AbstractT]):
    @abc.abstractmethod
    async def get_by_id(self, object_id: int) -> T | None:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def search_by(
        self,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        terms: str | None = None,
        filter_: AbstractT | None = None,
    ) -> tuple[list[T], int]:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def create(self, object_to_create: AbstractT) -> T:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def update(self, object_to_update: AbstractT, override: bool = False) -> T:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def delete(self, object_id: int) -> T:
        pass  # pragma: no cover
