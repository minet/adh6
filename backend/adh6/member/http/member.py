from typing import Any

from adh6.authentication.enums import Roles
from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.context import get_roles, get_user
from adh6.decorator import log_call, with_context
from adh6.default import DefaultHandler
from adh6.entity import AbstractMember, Comment, Member, MemberBody, MemberFilter, SubscriptionBody
from adh6.exceptions import NotFoundError, UnauthorizedError
from adh6.misc import handle_error

from ..charter_manager import CharterManager
from ..member_manager import MemberManager
from ..subscription_manager import SubscriptionManager


class MemberHandler(DefaultHandler):
    def __init__(
        self, member_manager: MemberManager, charter_manager: CharterManager, subscription_manager: SubscriptionManager
    ):
        super().__init__(Member, AbstractMember, member_manager)
        self.member_manager = member_manager
        self.charter_manager = charter_manager
        self.subscription_manager = subscription_manager

    @with_context
    @log_call
    async def search(
        self,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        terms: str | None = None,
        filter_: Any | None = None,
    ):
        filter_ = MemberFilter.from_dict(filter_) if filter_ else None
        result, total_count = await self.main_manager.search(limit=limit, offset=offset, terms=terms, filter_=filter_)
        headers = {"X-Total-Count": str(total_count), "access-control-expose-headers": "X-Total-Count"}
        return result, 200, headers

    @with_context
    @log_call
    async def get(self, id_: int, only: list[str] | None = None):
        try:

            def remove(entity: Any) -> Any:
                if isinstance(entity, dict) and only is not None:
                    entity_cp = entity.copy()
                    for k in entity_cp:
                        if k not in [*only, "id"]:
                            del entity[k]
                return entity

            obj = await self.main_manager.get_by_id(id=id_)
            return remove(obj.to_dict()), 200
        except Exception as e:
            if isinstance(e, NotFoundError) and Roles.ADMIN_READ.value not in get_roles():
                e = UnauthorizedError("cannot access this resource")
            raise e  # noqa: TRY201

    @with_context
    @log_call
    async def post(self, body):
        member_body = MemberBody.from_dict(body)
        if member_body is None:
            raise UnauthorizedError("Invalid body")
        created = await self.member_manager.create(member_body)
        return created.id, 201

    @with_context
    @log_call
    async def patch(self, id_, body):
        member_body = MemberBody.from_dict(body)
        if member_body is None:
            raise UnauthorizedError("Invalid body")
        await self.member_manager.update(id_, member_body)
        return None, 204

    @with_context
    @log_call
    async def subscription_post(self, id_: int, body: dict):
        """Add a membership record in the database"""
        sub_body = SubscriptionBody.from_dict(body)
        if sub_body is None:
            raise UnauthorizedError("Invalid body")
        created_membership = await self.subscription_manager.create(id_, sub_body)
        return created_membership.to_dict(), 200  # 200 OK

    @with_context
    @log_call
    async def password_put(self, id_, body):
        """Set the password of a member."""
        try:
            await self.member_manager.change_password(id_, body.get("password"), body.get("hashedPassword"))
        except Exception as e:
            if isinstance(e, NotFoundError) and Roles.ADMIN_WRITE.value not in get_roles():
                e = UnauthorizedError("cannot access this resource")
            raise e  # noqa: TRY201
        else:
            return None, 204  # 204 No Content

    @with_context
    @log_call
    async def logs_search(self, id_, dhcp=False, limit=10, offset=0):
        """Get logs from a member."""
        return await self.member_manager.get_logs(id_, limit=limit, offset=offset, dhcp=dhcp), 200

    @with_context
    @log_call
    async def statuses_search(self, id_: int):
        try:
            return [x.to_dict() for x in await self.member_manager.get_statuses(id_)], 200
        except Exception as e:
            if isinstance(e, NotFoundError) and Roles.ADMIN_READ.value not in get_roles():
                e = UnauthorizedError("cannot access this resource")
            raise e  # noqa: TRY201

    @with_context
    @log_call
    async def subscription_patch(self, id_, body):
        sub_body = SubscriptionBody.from_dict(body)
        if sub_body is None:
            raise UnauthorizedError("Invalid body")
        await self.subscription_manager.update(id_, sub_body)
        return None, 204

    @with_context
    @log_call
    async def subscription_validate(self, id_: int, free: bool = False):
        await self.subscription_manager.validate(id_, free)
        await self.member_manager.update_subnet(id_)
        return None, 204

    @with_context
    @log_call
    async def charter_get(self, id_, charter_id) -> tuple[Any, int]:
        if get_user() != id_ and Roles.ADMIN_READ.value not in get_roles():
            raise UnauthorizedError("Unauthorize to access this resource")
        return await self.charter_manager.get(charter_id=charter_id, member_id=id_), 200

    @with_context
    @log_call
    async def charter_put(self, id_, charter_id) -> tuple[Any, int]:
        try:
            if get_user() != id_ and Roles.ADMIN_READ.value not in get_roles():
                raise UnauthorizedError("Unauthorize to access this resource")  # noqa: TRY301
            await self.charter_manager.sign(charter_id=charter_id, member_id=id_)
        except Exception as e:
            return handle_error(e)
        else:
            return None, 204

    @with_context
    @log_call
    async def comment_put(self, id_, body):
        """Set the comment of a member."""
        try:
            comment = Comment.from_dict(body)
            if comment is None:
                return handle_error(UnauthorizedError("Invalid body"))
            await self.member_manager.change_comment(id_, comment)
        except Exception as e:
            return handle_error(e)
        else:
            return None, 204  # 204 No Content

    @with_context
    @log_call
    async def comment_search(self, id_):
        try:
            obj = await self.member_manager.get_comment(member_id=id_)
            return obj.to_dict(), 200
        except Exception as e:
            return handle_error(e)
