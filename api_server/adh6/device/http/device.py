# coding=utf-8
import typing as t
from connexion.decorators.produces import NoContent
from adh6.authentication import Roles
from adh6.constants import CTX_ADMIN, CTX_ROLES, DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity import AbstractDevice, Device, DeviceFilter, DeviceBody
from adh6.decorator import log_call, with_context
from adh6.default.http_handler import DefaultHandler
from adh6.exceptions import NotFoundError, UnauthorizedError

from ..device_manager import DeviceManager


class DeviceHandler(DefaultHandler):
    def __init__(self, device_manager: DeviceManager):
        super().__init__(Device, AbstractDevice, device_manager)
        self.device_manager = device_manager

    @with_context
    @log_call
    def post(self, ctx, body: dict = {}):
        device_body = DeviceBody.from_dict(body)
        if ctx.get(CTX_ADMIN) != device_body.member and Roles.ADMIN_WRITE.value not in ctx.get(CTX_ROLES, []):
            raise UnauthorizedError("Unauthorize to access this resource") 
        return self.device_manager.create(ctx, device_body).id, 201

    @with_context
    @log_call
    def search(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, filter_: dict = {}):
        device_filter = DeviceFilter.from_dict(filter_)
        if ctx.get(CTX_ADMIN) != device_filter.member and Roles.ADMIN_READ.value not in ctx.get(CTX_ROLES, []):
            raise UnauthorizedError("Unauthorize to access this resource")
        result, total_count = self.device_manager.search(ctx, limit=limit, offset=offset, device_filter=device_filter)
        headers = {
            "X-Total-Count": str(total_count),
            'access-control-expose-headers': 'X-Total-Count'
        }
        return result, 200, headers

    @with_context
    @log_call
    def get(self, ctx, id_: int, only: t.Optional[t.List[str]]=None):
        try:
            device = self.device_manager.get_by_id(ctx, id=id_)
            if ctx.get(CTX_ADMIN) != device.member and Roles.ADMIN_READ.value not in ctx.get(CTX_ROLES, []):
                raise UnauthorizedError("Unauthorize to access this resource")
            def remove(entity: t.Any) -> t.Any:
                if isinstance(entity, dict) and only is not None:
                    entity_cp = entity.copy()
                    for k in entity_cp.keys():
                        if k not in only + ["id"]:
                            del entity[k]
                return entity
            return remove(device.to_dict()), 200
        except Exception as e:
            if isinstance(e, NotFoundError) and Roles.ADMIN_READ.value not in ctx.get(CTX_ROLES):
                e = UnauthorizedError("cannot access this resource")
            raise e

    @with_context
    @log_call
    def delete(self, ctx, id_: int):
        try: 
            if ctx.get(CTX_ADMIN) != self.device_manager.get_owner(ctx, id_) and Roles.ADMIN_WRITE.value not in ctx.get(CTX_ROLES, []):
                raise UnauthorizedError("Unauthorize to access this resource")
            self.main_manager.delete(ctx, id=id_)
            return NoContent, 204  # 204 No Content
        except Exception as e:
            if isinstance(e, NotFoundError) and Roles.ADMIN_WRITE.value not in ctx.get(CTX_ROLES):
                e = UnauthorizedError("cannot access this resource")
            raise e
    
    @with_context
    @log_call
    def vendor_search(self, ctx, id_: int):
        """ Return the vendor associated with the given device """
        try:
            device = self.device_manager.get_by_id(ctx=ctx, id=id_)
            if ctx.get(CTX_ADMIN) != device.member and Roles.ADMIN_READ.value not in ctx.get(CTX_ROLES, []):
                raise UnauthorizedError("Unauthorize to access this resource")
            return self.device_manager.get_mac_vendor(ctx, id=id_), 200
        except Exception as e:
            if isinstance(e, NotFoundError) and Roles.ADMIN_READ.value not in ctx.get(CTX_ROLES):
                e = UnauthorizedError("cannot access this resource")
            raise e

    @with_context
    @log_call
    def mab_search(self, ctx, id_: int):
        """ Return the vendor associated with the given device """
        return self.device_manager.get_mab(ctx, id=id_), 200

    @with_context
    @log_call
    def mab_post(self, ctx, id_: int):
        """ Return the vendor associated with the given device """
        return self.device_manager.put_mab(ctx, id=id_), 200

    @with_context
    @log_call
    def member_search(self, ctx, id_: int):
        return self.device_manager.get_owner(ctx=ctx, device_id=id_), 200
