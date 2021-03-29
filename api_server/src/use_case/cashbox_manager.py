# coding=utf-8
""" Use cases (business rule layer) of everything related to the cashbox. """
from src.entity.roles import Roles
from src.use_case.decorator.security import SecurityDefinition, defines_security, uses_security
from src.use_case.interface.cashbox_repository import CashboxRepository
from src.use_case.interface.transaction_repository import TransactionRepository
from src.util.context import log_extra
from src.util.log import LOG


@defines_security(SecurityDefinition(
    item={
        "read": Roles.ADH6_ADMIN,
        "update": Roles.ADH6_ADMIN | Roles.ADH6_TRESO
    },
    collection={
        "read": Roles.ADH6_ADMIN
    }
))
class CashboxManager:
    """
    Implements all the use cases related to cashbox management.
    """

    def __init__(self,
                 cashbox_repository: CashboxRepository,
                 transaction_repository: TransactionRepository
                 ):
        self.cashbox_repository = cashbox_repository
        self.transaction_repository = transaction_repository

    @uses_security("read", is_collection=False)
    def get_cashbox(self, ctx) -> (int, int):
        fond, coffre = self.cashbox_repository.get_cashbox(ctx)

        # Log action.
        LOG.info('cashbox_get', extra=log_extra(
            ctx
        ))
        return fond, coffre

    @uses_security("update", is_collection=False)
    def update_cashbox(self, ctx, value_modifier=None, transaction=None) -> bool:
        """
        search transactions in the database.

        :raise IntMustBePositiveException
        """

        self.cashbox_repository.update_cashbox(ctx, value_modifier=value_modifier, transaction=transaction)
        #result, count = self.transaction_repository.search_transaction_by(ctx,
        #                                                                  limit=limit,
        #                                                                  offset=offset,
        #                                                                  account_id=account_id,
        #                                                                  terms=terms)

        # Log action.
        LOG.info('cashbox_update', extra=log_extra(
            ctx,
            value_modifier=value_modifier,
            transaction=transaction,
        ))
        return True
