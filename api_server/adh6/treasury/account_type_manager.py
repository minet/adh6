# coding=utf-8

from adh6.entity.account_type import AccountType
from adh6.exceptions import AccountTypeNotFoundError
from adh6.default.crud_manager import CRUDManager
from adh6.treasury.interfaces.account_type_repository import AccountTypeRepository


class AccountTypeManager(CRUDManager):
    def __init__(self, account_type_repository: AccountTypeRepository):
        super().__init__(account_type_repository, AccountType, AccountTypeNotFoundError)
        self.account_type_repository = account_type_repository
