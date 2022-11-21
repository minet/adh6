# coding=utf-8
from adh6.decorator import log_call, with_context
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
        balance = self.account_manager.get_cav_balance(ctx)
        return {'expectedCav': balance}, 200

    @with_context
    @log_call
    def get_cashbox(self, ctx):
        fond, coffre = self.cashbox_manager.get_cashbox(ctx)
        return {"fond": fond, "coffre": coffre}, 200
