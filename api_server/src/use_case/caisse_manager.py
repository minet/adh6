# coding=utf-8
""" Use cases (business rule layer) of everything related to the caisse. """

from src.use_case.interface.caisse_repository import CaisseRepository
from src.use_case.interface.transaction_repository import TransactionRepository
from src.util.context import log_extra
from src.util.log import LOG


class TreasuryManager:
    """
    Implements all the use cases related to caisse management.
    """

    def __init__(self,
                 caisse_repository: CaisseRepository,
                 transaction_repository: TransactionRepository
                 ):
        self.caisse_repository = caisse_repository
        self.transaction_repository = transaction_repository

    def get_caisse(self, ctx) -> (int, int):
        """
        User story: As an admin, I can see the details of a transaction.

        :raise TransactionNotFound
        """
        fond, coffre = self.caisse_repository.get_caisse(ctx)

        # Log action.
        LOG.info('caisse_get', extra=log_extra(
            ctx
        ))
        return fond, coffre

    def update_caisse(self, ctx, value=None, transaction=None) -> bool:
        """
        search transactions in the database.

        :raise IntMustBePositiveException
        """

        self.caisse_repository.update_caisse(ctx, value_modifier=value, transaction=transaction)
        #result, count = self.transaction_repository.search_transaction_by(ctx,
        #                                                                  limit=limit,
        #                                                                  offset=offset,
        #                                                                  account_id=account_id,
        #                                                                  terms=terms)

        # Log action.
        LOG.info('caisse_updaye', extra=log_extra(
            ctx,
            value=value,
            transaction=transaction,
        ))
        return True
