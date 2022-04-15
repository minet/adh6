# coding=utf-8
from src.entity import AbstractDevice, Device
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.http_api.default import DefaultHandler
from src.interface_adapter.http_api.util.error import handle_error
from src.interface_adapter.sql.decorator.sql_session import require_sql
from src.use_case.device_manager import DeviceManager


class DeviceHandler(DefaultHandler):
    def __init__(self, device_manager: DeviceManager):
        super().__init__(Device, AbstractDevice, device_manager)
        self.device_manager = device_manager

    @with_context
    @require_sql
    @log_call
    def vendor_get(self, ctx, id_=None):
        """ Return the vendor associated with the given device """
        try:
            return self.device_manager.get_mac_vendor(ctx, id=id_), 200
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @require_sql
    @log_call
    def device_mab_get(self, ctx, id_: int):
        """ Return the vendor associated with the given device """
        try:
            return self.device_manager.get_mab(ctx, id=id_), 200
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @require_sql
    @log_call
    def device_mab_put(self, ctx, id_: int):
        """ Return the vendor associated with the given device """
        try:
            return self.device_manager.put_mab(ctx, id=id_), 200
        except Exception as e:
            return handle_error(ctx, e)
