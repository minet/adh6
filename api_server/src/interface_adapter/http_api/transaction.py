# coding=utf-8

from src.entity import AbstractTransaction, Transaction
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.http_api.default import DefaultHandler
from src.interface_adapter.sql.decorator.sql_session import require_sql
from src.use_case.transaction_manager import TransactionManager


class TransactionHandler(DefaultHandler):
    def __init__(self, transaction_manager: TransactionManager):
        super().__init__(Transaction, AbstractTransaction, transaction_manager)

    @with_context
    @require_sql
    @log_call
    def upload_post(self, ctx, body):
        pass
