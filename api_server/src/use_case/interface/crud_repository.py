# coding=utf-8
import abc
from typing import List, Tuple

from src.constants import DEFAULT_LIMIT, DEFAULT_OFFSET


class CRUDRepository(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, filter_=None) -> Tuple[List, int]:
        pass

    @abc.abstractmethod
    def create(self, ctx, object_to_create) -> object:
        pass

    @abc.abstractmethod
    def update(self, ctx, object_to_update, override=False) -> object:
        pass

    @abc.abstractmethod
    def delete(self, ctx, object_id) -> None:
        pass
