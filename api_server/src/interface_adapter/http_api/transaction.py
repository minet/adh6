# coding=utf-8
from dataclasses import asdict

from connexion import NoContent

from src.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity.transaction import Transaction
from src.exceptions import UserInputError, TransactionNotFoundError
from src.interface_adapter.http_api.account import _map_account_to_http_response
from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.http_api.member import _map_member_to_http_response
from src.interface_adapter.http_api.payment_method import _map_payment_method_to_http_response
from src.interface_adapter.http_api.util.error import bad_request
from src.interface_adapter.sql.decorator.auth import auth_regular_admin
from src.interface_adapter.sql.decorator.sql_session import require_sql
from src.use_case.caisse_manager import CaisseManager
from src.use_case.member_manager import MemberManager
from src.use_case.payment_method_manager import PaymentMethodManager
from src.use_case.transaction_manager import TransactionManager, PartialMutationRequest, FullMutationRequest
from src.util.context import log_extra
from src.util.log import LOG


class TransactionHandler:
    def __init__(self, transaction_manager: TransactionManager, payment_method_manager: PaymentMethodManager,
                 member_manager: MemberManager,
                 caisse_manager: CaisseManager):
        self.transaction_manager = transaction_manager
        self.payment_method_manager = payment_method_manager
        self.caisse_manager = caisse_manager
        self.member_manager = member_manager

    @with_context
    @require_sql
    @auth_regular_admin
    def search(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, account=None, terms=None):
        """ Search all the member. """
        LOG.debug("http_transaction_search_called", extra=log_extra(ctx,
                                                                    limit=limit,
                                                                    offset=offset,
                                                                    account_id=account,
                                                                    terms=terms))
        try:
            result, total_count = self.transaction_manager.search(ctx, limit, offset, account, terms)
            headers = {
                "X-Total-Count": str(total_count),
                'access-control-expose-headers': 'X-Total-Count'
            }
            result = list(map(_map_transaction_to_http_response, result))
            return result, 200, headers  # 200 OK

        except UserInputError as e:
            return bad_request(e), 400  # 400 Bad Request

    @with_context
    @require_sql
    @auth_regular_admin
    def get(self, ctx, transaction_id):
        """ Get a specific transaction. """
        LOG.debug("http_transaction_get_called", extra=log_extra(ctx, transaction_id=transaction_id))
        try:
            return _map_transaction_to_http_response(
                self.transaction_manager.get_by_id(ctx, transaction_id)), 200  # 200 OK

        except TransactionNotFoundError:
            return NoContent, 404  # 404 Not Found

    @with_context
    @require_sql
    @auth_regular_admin
    def post(self, ctx, body):
        """ Add a transaction record in the database """
        LOG.debug("http_transaction_post_called", extra=log_extra(ctx, request=body))

        mutation_request = _map_http_request_to_full_mutation_request(body)

        try:
            created = self.transaction_manager.update_or_create(ctx, mutation_request)
            if created:
                caisse, count = self.payment_method_manager.search(ctx, limit=1, terms='Liquide')
                if mutation_request.paymentMethod == caisse[0].payment_method_id:
                    if body.get('caisse') == "to":
                        created = self.caisse_manager.update(ctx, value=mutation_request.value)
                    elif body.get('caisse') == "from":
                        created = self.caisse_manager.update(ctx, value=-mutation_request.value)

            if created:
                return NoContent, 201  # 201 Created
            else:
                return NoContent, 204  # 204 No Content

        except UserInputError as e:
            return bad_request(e), 400  # 400 Bad Request

    @with_context
    @require_sql
    @auth_regular_admin
    def patch(self, ctx, transaction_id, body):
        pass

    @with_context
    @require_sql
    @auth_regular_admin
    def upload_post(self, ctx, body):
        pass


def _map_transaction_to_http_response(transaction: Transaction) -> dict:
    fields = {
        "src": _map_account_to_http_response(transaction.src),
        "dst": _map_account_to_http_response(transaction.dst),
        "timestamp": transaction.timestamp,
        "name": transaction.name,
        "paymentMethod": _map_payment_method_to_http_response(transaction.paymentMethod),
        "value": transaction.value,
        "attachments": transaction.attachments,
        "author": _map_member_to_http_response(transaction.author)
    }

    return {k: v for k, v in fields.items() if v is not None}


def _map_http_request_to_partial_mutation_request(body) -> PartialMutationRequest:
    return PartialMutationRequest(
        src=body.get('src'),
        dst=body.get('dst'),
        name=body.get('name'),
        paymentMethod=body.get('payment_method'),
        value=body.get('value'),
    )


def _map_http_request_to_full_mutation_request(body) -> FullMutationRequest:
    partial = _map_http_request_to_partial_mutation_request(body)
    return FullMutationRequest(**asdict(partial))
