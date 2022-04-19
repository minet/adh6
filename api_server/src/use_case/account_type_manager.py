# coding=utf-8

from src.entity.account_type import AccountType
from src.exceptions import AccountTypeNotFoundError
from src.use_case.crud_manager import CRUDManager
from src.use_case.decorator.security import SecurityDefinition, defines_security, Roles, has_any_role
from src.use_case.interface.account_type_repository import AccountTypeRepository


@defines_security(SecurityDefinition(
    item={
        "read": has_any_role([Roles.USER])
    },
    collection={
        "read": has_any_role([Roles.USER])
    }
))
class AccountTypeManager(CRUDManager):
    def __init__(self, account_type_repository: AccountTypeRepository):
        super().__init__(account_type_repository, AccountType, AccountTypeNotFoundError)
        self.account_type_repository = account_type_repository
