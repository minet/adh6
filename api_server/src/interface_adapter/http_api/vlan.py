# coding=utf-8
from connexion import NoContent

from src.interface_adapter.http_api.util.serializer import serialize_response
from src.interface_adapter.http_api.util.error import handle_error
from src.entity import AbstractVlan, Vlan
from src.exceptions import PortNotFoundError, SwitchNotFoundError
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.http_api.default import DefaultHandler
from src.interface_adapter.sql.decorator.sql_session import require_sql
from src.use_case.vlan_manager import VLANManager
from src.util.context import log_extra
from src.util.log import LOG


class VLANHandler(DefaultHandler):
    def __init__(self, vlan_manager: VLANManager):
        super().__init__(Vlan, AbstractVlan, vlan_manager)
        self.vlan_manager = vlan_manager

    @with_context
    @require_sql
    @log_call
    def get_from_number(self, ctx, vlan_number):
        """ Get the state of a port """
        try:
            return serialize_response(self.vlan_manager.get_from_number(ctx, vlan_number))
        except Exception as e:
            return handle_error(e)
