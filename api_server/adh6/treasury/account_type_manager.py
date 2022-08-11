# coding=utf-8

from adh6.exceptions import AccountTypeNotFoundError
from adh6.default.crud_manager import CRUDManager
from adh6.treasury.interfaces.account_type_repository import AccountTypeRepository


class AccountTypeManager(CRUDManager):
    def __init__(self, account_type_repository: AccountTypeRepository):
        super().__init__(account_type_repository, AccountTypeNotFoundError)
