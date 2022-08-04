# coding=utf-8
""" Use cases (business rule layer) of everything related to the cashbox. """
from typing import Tuple
from adh6.treasury.interfaces.cashbox_repository import CashboxRepository
from adh6.misc.context import log_extra
from adh6.misc.log import LOG


class CashboxManager:
    """
    Implements all the use cases related to cashbox management.
    """

    def __init__(self, cashbox_repository: CashboxRepository):
        self.cashbox_repository = cashbox_repository

    def get_cashbox(self, ctx) -> Tuple[int, int]:
        fond, coffre = self.cashbox_repository.get(ctx)

        # Log action.
        LOG.info('cashbox_get', extra=log_extra(
            ctx
        ))
        return fond, coffre
