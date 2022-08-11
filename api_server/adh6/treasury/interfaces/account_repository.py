# coding=utf-8

from adh6.entity import Account, AbstractAccount
from adh6.default.crud_repository import CRUDRepository


class AccountRepository(CRUDRepository[Account, AbstractAccount]):
    pass  # pragma: no cover
