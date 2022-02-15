# coding=utf-8
import requests
from connexion import NoContent

from src.entity import AbstractDevice, Device
from src.exceptions import InvalidMACAddress, DeviceNotFoundError, ValidationError, UnauthenticatedError, \
    UnauthorizedError
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.http_api.default import DefaultHandler, _error
from src.interface_adapter.http_api.util.error import handle_error
from src.interface_adapter.sql.decorator.sql_session import require_sql
from src.use_case.device_manager import DeviceManager
from src.util.context import log_extra
from src.util.log import LOG
from src.util.validator import is_mac_address


class DeviceHandler(DefaultHandler):
    def __init__(self, device_manager: DeviceManager):
        super().__init__(Device, AbstractDevice, device_manager)
        self.device_manager = device_manager

    @with_context
    @require_sql
    @log_call
    def vendor_get(self, ctx, device_id=None):
        """ Return the vendor associated with the given device """
        try:
            return self.device_manager.get_mac_vendor(ctx, device_id=device_id), 200
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @require_sql
    @log_call
    def device_mab_get(self, ctx, device_id: int):
        """ Return the vendor associated with the given device """
        try:
            return self.device_manager.get_mab(ctx, device_id=device_id), 200
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @require_sql
    @log_call
    def device_mab_put(self, ctx, device_id: int):
        """ Return the vendor associated with the given device """
        try:
            return self.device_manager.put_mab(ctx, device_id=device_id), 200
        except Exception as e:
            return handle_error(ctx, e)