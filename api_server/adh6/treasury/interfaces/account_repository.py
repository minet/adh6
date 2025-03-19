# coding=utf-8

from adh6.default.crud_repository import CRUDRepository
from adh6.entity import AbstractAccount, Account


class AccountRepository(CRUDRepository[Account, AbstractAccount]):
    pass  # pragma: no cover
