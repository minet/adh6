# coding=utf-8
from src.entity import AbstractAccount, Account, Member
from src.entity.roles import Roles
from src.exceptions import AccountNotFoundError, UnauthorizedError
from src.use_case.crud_manager import CRUDManager
from src.use_case.decorator.auto_raise import auto_raise
from src.use_case.decorator.security import SecurityDefinition, defines_security, uses_security, owns
from src.use_case.interface.account_repository import AccountRepository


@defines_security(SecurityDefinition(
    item={
        "read": owns(Account.member) | owns(AbstractAccount.member) | Roles.ADH6_ADMIN
    },
    collection={
        "read": owns(Account.member) | owns(AbstractAccount.member) | Roles.ADH6_ADMIN
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
