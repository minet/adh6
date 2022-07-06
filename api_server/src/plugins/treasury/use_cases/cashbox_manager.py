# coding=utf-8
""" Use cases (business rule layer) of everything related to the cashbox. """
from typing import Tuple
from src.use_case.decorator.security import SecurityDefinition, Roles, defines_security, has_any_role, is_admin, uses_security
from src.plugins.treasury.interfaces.cashbox_repository import CashboxRepository
from src.util.context import log_extra
from src.util.log import LOG


@defines_security(SecurityDefinition(
    item={
        "read": is_admin(),
        "update": has_any_role([Roles.ADMIN, Roles.TRESO])
    },
    collection={
        "read": is_admin()
    }
))
class CashboxManager:
    """
    Implements all the use cases related to cashbox management.
    """

    def __init__(self, cashbox_repository: CashboxRepository):
        self.cashbox_repository = cashbox_repository

    @uses_security("read", is_collection=False)
    def get_cashbox(self, ctx) -> Tuple[int, int]:
        fond, coffre = self.cashbox_repository.get(ctx)

        # Log action.
        LOG.info('cashbox_get', extra=log_extra(
            ctx
        ))
        return fond, coffre
