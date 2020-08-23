# coding=utf-8

from src.entity.account_type import AccountType
from src.exceptions import AccountTypeNotFoundError
from src.use_case.crud_manager import CRUDManager
from src.use_case.interface.account_type_repository import AccountTypeRepository


class AccountTypeManager(CRUDManager):
    def __init__(self, account_type_repository: AccountTypeRepository):
        super().__init__('account_type', account_type_repository, AccountType, AccountTypeNotFoundError)
        self.account_type_repository = account_type_repository

