# coding=utf-8
import requests
from connexion import NoContent

from src.entity import AbstractDevice, Device
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.http_api.default import DefaultHandler
from src.interface_adapter.sql.decorator.auth import auth_regular_admin
from src.interface_adapter.sql.decorator.sql_session import require_sql
from src.use_case.device_manager import DeviceManager
from src.util.context import log_extra
from src.util.log import LOG


class DeviceHandler(DefaultHandler):
    def __init__(self, device_manager: DeviceManager):
        super().__init__(Device, AbstractDevice, device_manager)
        self.device_manager = device_manager

    @with_context
    @require_sql
    @auth_regular_admin
    @log_call
    def vendor_get(self, ctx, mac_address):
        """ Return the vendor associated with the macAddress """
        r = requests.get('https://macvendors.co/api/vendorname/' + str(mac_address))

        if r.status_code == 200:
            LOG.info("vendor_fetch", extra=log_extra(ctx, mac=mac_address))
            return {"vendorname": r.text}, 200

        else:
            return NoContent, 404
