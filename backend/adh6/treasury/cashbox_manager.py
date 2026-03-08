"""Use cases (business rule layer) of everything related to the cashbox."""

import logging

from .interfaces import CashboxRepository


class CashboxManager:
    """
    Implements all the use cases related to cashbox management.
    """

    def __init__(self, cashbox_repository: CashboxRepository):
        self.cashbox_repository = cashbox_repository

    async def get_cashbox(self) -> tuple[int, int]:
        fond, coffre = await self.cashbox_repository.get()
        logging.debug("cashbox_get")  # noqa: LOG015  # TODO: use a dedicated logger
        return fond, coffre
