# coding=utf-8
from src.entity import Account, AbstractAccount
from src.interface_adapter.http_api.default import DefaultHandler
from src.use_case.account_manager import AccountManager


class AccountHandler(DefaultHandler):
    def __init__(self, account_manager: AccountManager):
        super().__init__(Account, AbstractAccount, account_manager)
