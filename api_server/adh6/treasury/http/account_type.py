# coding=utf-8
from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.decorator import log_call, with_context
from adh6.treasury.account_type_manager import AccountTypeManager


class AccountTypeHandler:
    def __init__(self, account_type_manager: AccountTypeManager):
        self.account_type_manager = account_type_manager

    @with_context
    @log_call
    def search(self, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None):
        result, total_count = self.account_type_manager.search(limit=limit, offset=offset, terms=terms)
        headers = {
            "X-Total-Count": str(total_count),
            'access-control-expose-headers': 'X-Total-Count'
        }
        result = list(map(lambda x: x.to_dict(), result))
        return result, 200, headers

    @with_context
    @log_call
    def get(self, id_: int):
        return self.account_type_manager.get_by_id(id=id_).to_dict(), 200

