# coding=utf-8
from src.entity import AbstractAccount
from src.exceptions import AccountNotFoundError, UnauthorizedError
from src.use_case.crud_manager import CRUDManager
from src.use_case.decorator.auto_raise import auto_raise
from src.use_case.interface.account_repository import AccountRepository

@auto_raise
def _owner_check(filter_: AbstractAccount, admin_id):
    if filter_.member is not None and filter_.member != admin_id:
        raise UnauthorizedError("You may only read or write to your own accounts")
    filter_.member = admin_id


class AccountManager(CRUDManager):
    def __init__(self, account_repository: AccountRepository):
        super().__init__('account', account_repository, AbstractAccount, AccountNotFoundError, _owner_check)
        self.account_repository = account_repository

    def get_cav_balance(self, ctx):
        results, count = self.account_repository.search_by(ctx, filter_=AbstractAccount(compte_courant=True))
        return sum(list(map(lambda a: a.balance, results)))

