# coding=utf-8
from src.entity import AbstractAccount
from src.exceptions import AccountNotFoundError
from src.use_case.crud_manager import CRUDManager
from src.use_case.interface.account_repository import AccountRepository


class AccountManager(CRUDManager):
    def __init__(self, account_repository: AccountRepository):
        super().__init__('account', account_repository, AbstractAccount, AccountNotFoundError)
        self.account_repository = account_repository

    def get_cav_balance(self, ctx):
        results, count = self.account_repository.search_by(ctx, filter_=AbstractAccount(compte_courant=True))
        return sum(list(map(lambda a: a.balance, results)))

