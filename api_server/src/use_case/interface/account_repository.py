# coding=utf-8

from typing import List, Tuple

from src.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity import Account, AbstractAccount
from src.use_case.interface.crud_repository import CRUDRepository


class AccountRepository(CRUDRepository):
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None,
                  filter_: AbstractAccount = None) -> Tuple[List[Account], int]:
        raise NotImplementedError

    def create(self, ctx, object_to_create: Account) -> object:
        raise NotImplementedError

    def update(self, ctx, object_to_update: AbstractAccount, override=False) -> object:
        raise NotImplementedError

    def delete(self, ctx, object_id) -> None:
        raise NotImplementedError
