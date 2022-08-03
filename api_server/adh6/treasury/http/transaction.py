# coding=utf-8
from connexion import NoContent

from adh6.entity import AbstractTransaction, Transaction
from adh6.default.decorator.log_call import log_call
from adh6.default.decorator.with_context import with_context
from adh6.default.http_handler import DefaultHandler
from adh6.default.util.error import handle_error
from adh6.treasury.transaction_manager import TransactionManager


class TransactionHandler(DefaultHandler):
    def __init__(self, transaction_manager: TransactionManager):
        super().__init__(Transaction, AbstractTransaction, transaction_manager)
        self.transaction_manager = transaction_manager

    @with_context
    @log_call
    def upload_post(self, ctx, body):
        pass

    @with_context
    @log_call
    def validate(self, ctx, id_: int):
        try:
            self.transaction_manager.validate(ctx, id=id_)
            return NoContent, 204
        except Exception as e:
            return handle_error(ctx, e)
