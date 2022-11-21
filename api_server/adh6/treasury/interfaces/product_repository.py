# coding=utf-8
import abc
from typing import List, Optional, Tuple
from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity import AbstractProduct


class ProductRepository(abc.ABC):
    @abc.abstractmethod
    def get_by_id(self, object_id: int) -> AbstractProduct:
        pass  # pragma: no cover

    @abc.abstractmethod
    def search_by(self, limit: int = DEFAULT_LIMIT, offset: int = DEFAULT_OFFSET, terms: Optional[str] = None) -> Tuple[List[AbstractProduct], int]:
        pass  # pragma: no cover
