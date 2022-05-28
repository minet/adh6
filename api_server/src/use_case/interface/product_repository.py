# coding=utf-8
import abc
from typing import List, Optional, Tuple
from src.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity import AbstractProduct


class ProductRepository(abc.ABC):
    @abc.abstractmethod
    def get_by_id(self, ctx, object_id: int) -> AbstractProduct:
        pass  # pragma: no cover

    @abc.abstractmethod
    def search_by(self, ctx, limit: int = DEFAULT_LIMIT, offset: int = DEFAULT_OFFSET, terms: Optional[str] = None) -> Tuple[List[AbstractProduct], int]:
        pass  # pragma: no cover
