# coding=utf-8

from typing import List

from src.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity import PaymentMethod
from src.use_case.interface.crud_repository import CRUDRepository


class PaymentMethodRepository(CRUDRepository):
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None,
                  filter_: PaymentMethod = None) -> (List[PaymentMethod], int):
        raise NotImplementedError

    def create(self, ctx, object_to_create: PaymentMethod) -> object:
        raise NotImplementedError

    def update(self, ctx, object_to_update: PaymentMethod, override=False) -> object:
        raise NotImplementedError

    def delete(self, ctx, object_id) -> None:
        raise NotImplementedError
