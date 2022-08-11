# coding=utf-8
from adh6.default.decorator.log_call import log_call
from adh6.default.decorator.with_context import with_context
from adh6.default.util.error import handle_error
from adh6.treasury.account_manager import AccountManager
from adh6.treasury.cashbox_manager import CashboxManager


class TreasuryHandler:
    def __init__(self, cashbox_manager: CashboxManager,
                 account_manager: AccountManager):
        self.cashbox_manager = cashbox_manager
        self.account_manager = account_manager

    @with_context
    @log_call
    def get_bank(self, ctx):
        try:
            balance = self.account_manager.get_cav_balance(ctx)
            return {'expectedCav': balance}, 200
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def get_cashbox(self, ctx):
        try:
            fond, coffre = self.cashbox_manager.get_cashbox(ctx)
            return {"fond": fond, "coffre": coffre}, 200
        except Exception as e:
            return handle_error(ctx, e)
