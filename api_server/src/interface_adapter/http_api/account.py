# coding=utf-8
from dataclasses import asdict

from connexion import NoContent

from src.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity import AbstractAccount, Account
from src.exceptions import AccountNotFoundError, UserInputError
from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.http_api.default import DefaultHandler
from src.interface_adapter.http_api.util.error import bad_request
from src.interface_adapter.http_api.util.serializer import serialize_response
from src.interface_adapter.sql.decorator.auth import auth_regular_admin
from src.interface_adapter.sql.decorator.sql_session import require_sql
from src.use_case.account_manager import AccountManager
from src.use_case.transaction_manager import TransactionManager
from src.util.context import log_extra
from src.util.log import LOG


class AccountHandler(DefaultHandler):
    def __init__(self, account_manager: AccountManager, transaction_manager: TransactionManager):
        super().__init__(Account, AbstractAccount, account_manager)
        self.account_manager = account_manager
        self.transaction_manager = transaction_manager
