# coding=utf-8
import abc
import typing as t

from adh6.entity import AbstractProduct


class ProductRepository(abc.ABC):
    @abc.abstractmethod
    def get_by_id(self, object_id: int) -> AbstractProduct:
        pass  # pragma: no cover

    @abc.abstractmethod
    def search_by(self, limit: int, offset: int, terms: t.Optional[str] = None) -> t.Tuple[t.List[AbstractProduct], int]:
        pass  # pragma: no cover
