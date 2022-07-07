# coding=utf-8
from adh6.entity import AbstractAccount, Account
from adh6.exceptions import AccountNotFoundError
from adh6.default.crud_manager import CRUDManager
from adh6.authentication.security import SecurityDefinition, defines_security, is_admin, owns, uses_security
from adh6.treasury.interfaces.account_repository import AccountRepository


@defines_security(SecurityDefinition(
    item={
        "read": owns(Account.member.id) | owns(AbstractAccount.member) | is_admin()
    },
    collection={
        "read": owns(AbstractAccount.member) | is_admin()
    }
))
class AccountManager(CRUDManager):
    def __init__(self, account_repository: AccountRepository):
        super().__init__(account_repository, AbstractAccount, AccountNotFoundError)
        self.account_repository = account_repository

    @uses_security("read", is_collection=False)
    def get_cav_balance(self, ctx):
        results, _ = self.account_repository.search_by(ctx, filter_=AbstractAccount(compte_courant=True))
        return sum(list(map(lambda a: a.balance, results)))
