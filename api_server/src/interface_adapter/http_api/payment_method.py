# coding=utf-8
from connexion import NoContent

from src.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from src.exceptions import UserInputError, PaymentMethodNotFoundError
from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.http_api.util.error import bad_request
from src.interface_adapter.http_api.util.serializer import serialize_response
from src.interface_adapter.sql.decorator.auth import auth_regular_admin
from src.interface_adapter.sql.decorator.sql_session import require_sql
from src.use_case.payment_method_manager import PaymentMethodManager
from src.util.context import log_extra
from src.util.log import LOG


class PaymentMethodHandler:
    def __init__(self, payment_method_manager: PaymentMethodManager):
        self.payment_method_manager = payment_method_manager

    @with_context
    @require_sql
    @auth_regular_admin
    def search(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, filter_=None):
        """ Filter the list of the payment_method according to some criterias """
        LOG.debug("http_payment_method_search_called", extra=log_extra(ctx, limit=limit, offset=offset, terms=terms, filter_=filter_))

        try:
            result, count = self.payment_method_manager.search(ctx, limit=limit, offset=offset, terms=terms)

        except UserInputError as e:
            return bad_request(e), 400

        headers = {
            "X-Total-Count": count,
            "access-control-expose-headers": "X-Total-Count"
        }
        return list(map(serialize_response, result)), 200, headers

    @with_context
    @require_sql
    @auth_regular_admin
    def get(self, ctx, payment_method_id):
        """ Return the payment method specified by the id  """
        LOG.debug("http_payment_method_get_called", extra=log_extra(ctx, payment_method_id=payment_method_id))
        try:
            result = self.payment_method_manager.get_by_id(ctx, payment_method_id=payment_method_id)
            return serialize_response(result), 200  # OK

        except PaymentMethodNotFoundError:
            return NoContent, 404  # 404 Not Found
