# coding=utf-8
from adh6.entity import AbstractAccount, Account
from adh6.exceptions import AccountNotFoundError
from adh6.default.crud_manager import CRUDManager
from adh6.decorator import log_call

from .interfaces import AccountRepository


class AccountManager(CRUDManager):
    def __init__(self, account_repository: AccountRepository):
        super().__init__(account_repository, AccountNotFoundError)
        self.account_repository = account_repository

    @log_call
    def get_by_name(self, name: str) -> Account:
        a = self.account_repository.get_by_name(name)
        if not a:
            raise AccountNotFoundError(name)
        return a

    @log_call
    def get_by_member(self, member_id: int) -> Account:
        r, _ = self.account_repository.search_by(limit=1, filter_=AbstractAccount(member=member_id))
        if not r:
            raise AccountNotFoundError()
        return r[0]

    @log_call
    def get_cav_balance(self):
        results, _ = self.account_repository.search_by(filter_=AbstractAccount(compte_courant=True))
        return sum(list(map(lambda a: a.balance, results)))
