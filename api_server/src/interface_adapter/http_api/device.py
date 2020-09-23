# coding=utf-8
import requests
from connexion import NoContent

from src.entity import AbstractDevice, Device
from src.exceptions import InvalidMACAddress, DeviceNotFoundError
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.http_api.default import DefaultHandler
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
        device = None
        try:
            device = self.device_manager.get_by_id(ctx, device_id=device_id)
        except DeviceNotFoundError:
            return {
                'code': 404,
                'message': "Device not found"
            }

        r = requests.get('https://macvendors.co/api/vendorname/' + str(device.mac))

        if r.status_code == 200:
            return {"vendorname": r.text}, 200

        else:
            return NoContent, 404
