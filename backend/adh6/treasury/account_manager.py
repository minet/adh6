from adh6.default.crud_manager import CRUDManager
from adh6.entity import AbstractAccount
from adh6.exceptions import AccountNotFoundError

from .interfaces import AccountRepository


class AccountManager(CRUDManager):
    def __init__(self, account_repository: AccountRepository):
        super().__init__(account_repository, AccountNotFoundError)
        self.account_repository = account_repository

    async def get_cav_balance(self):
        results, _ = await self.account_repository.search_by(filter_=AbstractAccount(compteCourant=True))
        return sum(a.balance for a in results if a.balance is not None)
