# coding=utf-8
from dataclasses import asdict

from connexion import NoContent

from src.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity.transaction import Transaction
from src.exceptions import UserInputError, TransactionNotFoundError
from src.interface_adapter.http_api.account import _map_account_to_http_response
from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.http_api.payment_method import _map_payment_method_to_http_response
from src.interface_adapter.http_api.util.error import bad_request
from src.interface_adapter.sql.decorator.auth import auth_regular_admin
from src.interface_adapter.sql.decorator.sql_session import require_sql
from src.util.context import log_extra
from src.util.log import LOG


class BugReportHandler:

    @with_context
    @require_sql
    @auth_regular_admin
    def search(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, account=None, terms=None):
        return bad_request(), 400  # 400 Bad Request

    @with_context
    @require_sql
    @auth_regular_admin
    def get(self, ctx, transaction_id):
        return bad_request(), 400  # 400 Bad Request

    @with_context
    @require_sql
    @auth_regular_admin
    def post(self, ctx, body):
        return bad_request(), 400  # 400 Bad Request

    @with_context
    @require_sql
    @auth_regular_admin
    def put(self, ctx, transaction_id, body):
        pass


def _map_transaction_to_http_response(transaction: Transaction) -> dict:
    fields = {
        "src": _map_account_to_http_response(transaction.src),
        "dst": _map_account_to_http_response(transaction.dst),
        "timestamp": transaction.timestamp,
        "name": transaction.name,
        "paymentMethod": _map_payment_method_to_http_response(transaction.paymentMethod),
        "value": transaction.value,
        "attachments": transaction.attachments
    }

    return {k: v for k, v in fields.items() if v is not None}
