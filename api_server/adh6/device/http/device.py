# coding=utf-8
import typing as t
from connexion.decorators.produces import NoContent
from adh6.authentication import Roles
from adh6.context import get_roles, get_user, get_login
from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity import AbstractDevice, Device, DeviceFilter, DeviceBody
from adh6.decorator import log_call, with_context
from adh6.default.http_handler import DefaultHandler
from adh6.exceptions import NotFoundError, UnauthorizedError

from ..device_manager import DeviceManager
from ..device_logs_manager import DeviceLogsManager


class DeviceHandler(DefaultHandler):
    def __init__(self, device_manager: DeviceManager, device_logs_manager: DeviceLogsManager):
        super().__init__(Device, AbstractDevice, device_manager)
        self.device_manager = device_manager
        self.device_logs_manager = device_logs_manager

    @with_context
    @log_call
    def post(self, body: dict = {}):
        device_body = DeviceBody.from_dict(body)
        if get_user() != device_body.member and Roles.ADMIN_WRITE.value not in get_roles():
            raise UnauthorizedError("Unauthorize to access this resource") 
        return self.device_manager.create(device_body).id, 201

    @with_context
    @log_call
    def search(self, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, filter_: dict = {}):
        device_filter = DeviceFilter.from_dict(filter_)
        result, total_count = self.device_manager.search(limit=limit, offset=offset, device_filter=device_filter)
        headers = {
            "X-Total-Count": str(total_count),
            'access-control-expose-headers': 'X-Total-Count'
        }
        return result, 200, headers

    @with_context
    @log_call
    def get(self, id_: int, only: t.Optional[t.List[str]]=None):
        try:
            device = self.device_manager.get_by_id(id=id_)
            if get_user() != device.member and Roles.ADMIN_READ.value not in get_roles():
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
            if isinstance(e, NotFoundError) and Roles.ADMIN_READ.value not in get_roles():
                e = UnauthorizedError("cannot access this resource")
            raise e

    @with_context
    @log_call
    def delete(self, id_: int):
        try: 
            if get_user() != self.device_manager.get_owner(id_) and Roles.ADMIN_WRITE.value not in get_roles():
                raise UnauthorizedError("Unauthorize to access this resource")
            self.main_manager.delete(id=id_)
            return NoContent, 204  # 204 No Content
        except Exception as e:
            if isinstance(e, NotFoundError) and Roles.ADMIN_WRITE.value not in get_roles():
                e = UnauthorizedError("cannot access this resource")
            raise e
    
    @with_context
    @log_call
    def vendor_search(self, id_: int):
        """ Return the vendor associated with the given device """
        try:
            device = self.device_manager.get_by_id(id=id_)
            if get_user() != device.member and Roles.ADMIN_READ.value not in get_roles():
                raise UnauthorizedError("Unauthorize to access this resource")
            return self.device_manager.get_mac_vendor(id=id_), 200
        except Exception as e:
            if isinstance(e, NotFoundError) and Roles.ADMIN_READ.value not in get_roles():
                e = UnauthorizedError("cannot access this resource")
            raise e

    @with_context
    @log_call
    def mab_search(self, id_: int):
        """ Return the vendor associated with the given device """
        return self.device_manager.get_mab(id=id_), 200

    @with_context
    @log_call
    def mab_post(self, id_: int):
        """ Return the vendor associated with the given device """
        return self.device_manager.put_mab(id=id_), 200

    @with_context
    @log_call
    def member_search(self, id_: int):
        return self.device_manager.get_owner(device_id=id_), 200

    @with_context
    @log_call
    def member_get(self, login: str, connection_type: str):
        """ Get logs from a member. """
        if get_login() != login and Roles.ADMIN_READ.value not in get_roles():
            raise UnauthorizedError("Unauthorize to access this resource")
        devices = self.device_manager.get_by_user_login(login, connection_type)
        headers = {
            "X-Total-Count": str(len(devices)),
            'access-control-expose-headers': 'X-Total-Count'
        }
        return devices, 200, headers

    @with_context
    @log_call
    def member_logs_search(self, login, dhcp=False):
        """ Get logs from a member. """
        return self.device_logs_manager.get_logs(login=login, dhcp=dhcp), 200

    @with_context
    @log_call
    def member_statuses_search(self, login: int):
        try:
            return list(map(lambda x: x.to_dict(), self.device_logs_manager.get_statuses(login))), 200
        except Exception as e:
            if isinstance(e, NotFoundError) and Roles.ADMIN_READ.value not in get_roles():
                e = UnauthorizedError("cannot access this resource")
            raise e
