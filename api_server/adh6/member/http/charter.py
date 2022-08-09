from connexion import NoContent
from adh6.default.decorator.with_context import with_context
from adh6.default.util.error import handle_error
from adh6.member.charter_manager import CharterManager


class CharterHandler:
    def __init__(self, charter_manager: CharterManager) -> None:
        self.charter_manager = charter_manager

    @with_context
    def member_search(self, ctx, charter_id: int):
        result, total_count = self.charter_manager.get_members(ctx, charter_id)
        headers = {
            "X-Total-Count": str(total_count),
            'access-control-expose-headers': 'X-Total-Count'
        }
        return result, 200, headers

    @with_context
    def member_post(self, ctx, charter_id: int, id_: int):
        try: 
            self.charter_manager.sign(ctx, charter_id, id_)
            return NoContent, 201
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    def member_get(self, ctx, charter_id: int, id_: int):
        try: 
            return self.charter_manager.get(ctx, charter_id, id_), 200
        except Exception as e:
            return handle_error(ctx, e)
