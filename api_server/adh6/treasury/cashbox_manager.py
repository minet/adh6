"""Use cases (business rule layer) of everything related to the cashbox."""

import logging
from typing import Tuple

from .interfaces import CashboxRepository


class CashboxManager:
    """
    Implements all the use cases related to cashbox management.
    """

    def __init__(self, cashbox_repository: CashboxRepository):
        self.cashbox_repository = cashbox_repository

    def get_cashbox(self) -> Tuple[int, int]:
        fond, coffre = self.cashbox_repository.get()
        logging.debug("cashbox_get")
        return fond, coffre
