# coding=utf-8
from adh6.entity import AbstractAccount
from adh6.exceptions import AccountNotFoundError
from adh6.default.crud_manager import CRUDManager
from adh6.treasury.interfaces.account_repository import AccountRepository


class AccountManager(CRUDManager):
    def __init__(self, account_repository: AccountRepository):
        super().__init__(account_repository, AbstractAccount, AccountNotFoundError)
        self.account_repository = account_repository

    def get_cav_balance(self, ctx):
        results, _ = self.account_repository.search_by(ctx, filter_=AbstractAccount(compte_courant=True))
        return sum(list(map(lambda a: a.balance, results)))
