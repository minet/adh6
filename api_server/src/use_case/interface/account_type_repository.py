# coding=utf-8

from typing import List, Tuple

from src.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity import AccountType
from src.use_case.interface.crud_repository import CRUDRepository


class AccountTypeRepository(CRUDRepository):
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None,
                  filter_: AccountType = None) -> Tuple[List[AccountType], int]:
        raise NotImplemented

    def create(self, ctx, object_to_create: AccountType) -> object:
        raise NotImplemented

    def update(self, ctx, object_to_update: AccountType, override=False) -> object:
        raise NotImplemented

    def delete(self, ctx, object_id) -> None:
        raise NotImplemented
