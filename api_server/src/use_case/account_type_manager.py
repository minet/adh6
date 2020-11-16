# coding=utf-8

from src.entity.account_type import AccountType
from src.entity.roles import Roles
from src.exceptions import AccountTypeNotFoundError
from src.use_case.crud_manager import CRUDManager
from src.use_case.decorator.security import SecurityDefinition, defines_security
from src.use_case.interface.account_type_repository import AccountTypeRepository


@defines_security(SecurityDefinition(
    item={
        "read": Roles.ADH6_USER
    },
    collection={
        "read": Roles.ADH6_USER
    }
))
class AccountTypeManager(CRUDManager):
    def __init__(self, account_type_repository: AccountTypeRepository):
        super().__init__('account_type', account_type_repository, AccountType, AccountTypeNotFoundError)
        self.account_type_repository = account_type_repository
