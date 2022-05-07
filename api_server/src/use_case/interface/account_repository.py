# coding=utf-8

from src.entity import Account, AbstractAccount
from src.use_case.interface.crud_repository import CRUDRepository


class AccountRepository(CRUDRepository[Account, AbstractAccount]):
    pass  # pragma: no cover
