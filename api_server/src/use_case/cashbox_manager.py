# coding=utf-8
""" Use cases (business rule layer) of everything related to the cashbox. """

from src.use_case.interface.cashbox_repository import CashboxRepository
from src.use_case.interface.transaction_repository import TransactionRepository
from src.util.context import log_extra
from src.util.log import LOG


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

    def get_cashbox(self, ctx) -> (int, int):
        fond, coffre = self.cashbox_repository.get_cashbox(ctx)

        # Log action.
        LOG.info('cashbox_get', extra=log_extra(
            ctx
        ))
        return fond, coffre

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
