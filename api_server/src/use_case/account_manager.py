# coding=utf-8
from src.entity import AbstractAccount, Admin, Account
from src.entity.roles import Roles
from src.exceptions import AccountNotFoundError, UnauthorizedError
from src.use_case.crud_manager import CRUDManager
from src.use_case.decorator.auto_raise import auto_raise
from src.use_case.decorator.security import SecurityDefinition, defines_security, uses_security
from src.use_case.interface.account_repository import AccountRepository


@defines_security(SecurityDefinition(
    item={
        "read": (Account.member.id == Admin.member) | (AbstractAccount.member == Admin.member) | Roles.ADMIN
    },
    collection={
        "read": (AbstractAccount.member == Admin.member) | Roles.ADMIN
    }
))
class AccountManager(CRUDManager):
    def __init__(self, account_repository: AccountRepository):
        super().__init__('account', account_repository, AbstractAccount, AccountNotFoundError)
        self.account_repository = account_repository

    @uses_security("read", is_collection=False)
    def get_cav_balance(self, ctx):
        results, count = self.account_repository.search_by(ctx, filter_=AbstractAccount(compte_courant=True))
        return sum(list(map(lambda a: a.balance, results)))
