# coding=utf-8
from connexion import NoContent

from src.entity import AbstractTransaction, Transaction
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.http_api.default import DefaultHandler
from src.interface_adapter.http_api.util.error import handle_error
from src.interface_adapter.sql.decorator.sql_session import require_sql
from src.use_case.transaction_manager import TransactionManager


class TransactionHandler(DefaultHandler):
    def __init__(self, transaction_manager: TransactionManager):
        super().__init__(Transaction, AbstractTransaction, transaction_manager)
        self.transaction_manager = transaction_manager

    @with_context
    @require_sql
    @log_call
    def upload_post(self, ctx, body):
        pass

    @with_context
    @require_sql
    @log_call
    def validate(self, ctx, id_=None):
        try:
            self.transaction_manager.validate(ctx, id=id_)
            return NoContent, 204
        except Exception as e:
            return handle_error(ctx, e)
