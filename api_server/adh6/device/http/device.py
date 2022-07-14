# coding=utf-8
import typing as t
from connexion.decorators.produces import NoContent
from adh6.authentication import Roles
from adh6.constants import CTX_ADMIN, CTX_ROLES
from adh6.default.util.serializer import serialize_response
from adh6.entity import AbstractDevice, Device
from adh6.default.decorator.log_call import log_call
from adh6.default.decorator.with_context import with_context
from adh6.default.http_handler import DefaultHandler
from adh6.default.util.error import handle_error
from adh6.device.device_manager import DeviceManager
from adh6.exceptions import UnauthorizedError


class DeviceHandler(DefaultHandler):
    def __init__(self, device_manager: DeviceManager):
        super().__init__(Device, AbstractDevice, device_manager)
        self.device_manager = device_manager
    
    @with_context
    @log_call
    def vendor_get(self, ctx, id_=None):
        """ Return the vendor associated with the given device """
        try:
            device = self.device_manager.get_by_id(ctx=ctx, id=id_)
            if ctx.get(CTX_ADMIN) != device.member and Roles.ADMIN_WRITE.value not in ctx.get(CTX_ROLES, []):
                raise UnauthorizedError("Unauthorize to access this resource")
            return self.device_manager.get_mac_vendor(ctx, id=id_), 200
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def device_mab_get(self, ctx, id_: int):
        """ Return the vendor associated with the given device """
        try:
            return self.device_manager.get_mab(ctx, id=id_), 200
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def device_mab_put(self, ctx, id_: int):
        """ Return the vendor associated with the given device """
        try:
            return self.device_manager.put_mab(ctx, id=id_), 200
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def get(self, ctx, id_: int, only: t.Optional[t.List[str]]=None):
        try:
            device = self.main_manager.get_by_id(ctx, id=id_)
            if ctx.get(CTX_ADMIN) != device.member and Roles.ADMIN_WRITE.value not in ctx.get(CTX_ROLES, []):
                raise UnauthorizedError("Unauthorize to access this resource")
            def remove(entity: t.Any) -> t.Any:
                if isinstance(entity, dict) and only is not None:
                    entity_cp = entity.copy()
                    for k in entity_cp.keys():
                        if k not in only + ["id", "__typename"]:
                            del entity[k]
                return entity
            return remove(serialize_response(device)), 200
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def delete(self, ctx, id_: int):
        try:
            device = self.device_manager.get_by_id(ctx=ctx, id=id_)
            if ctx.get(CTX_ADMIN) != device.member and Roles.ADMIN_WRITE.value not in ctx.get(CTX_ROLES, []):
                raise UnauthorizedError("Unauthorize to access this resource")
            self.main_manager.delete(ctx, id=id_)
            return NoContent, 204  # 204 No Content
        except Exception as e:
            return handle_error(ctx, e)
