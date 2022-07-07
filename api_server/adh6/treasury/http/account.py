# coding=utf-8
from adh6.entity import Account, AbstractAccount
from adh6.default.http_handler import DefaultHandler
from adh6.treasury.account_manager import AccountManager


class AccountHandler(DefaultHandler):
    def __init__(self, account_manager: AccountManager):
        super().__init__(Account, AbstractAccount, account_manager)
