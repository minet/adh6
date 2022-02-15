# coding=utf-8
from src.entity import AccountType
from src.interface_adapter.http_api.default import DefaultHandler
from src.use_case.account_type_manager import AccountTypeManager


class AccountTypeHandler(DefaultHandler):
    def __init__(self, account_type_manager: AccountTypeManager):
        super().__init__(AccountType, AccountType, account_type_manager)
