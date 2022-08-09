# coding=utf-8
from adh6.default.util.error import handle_error
from adh6.entity import AbstractVlan, Vlan
from adh6.default.decorator.log_call import log_call
from adh6.default.decorator.with_context import with_context
from adh6.default.http_handler import DefaultHandler
from adh6.subnet.vlan_manager import VlanManager

class VLANHandler(DefaultHandler):
    def __init__(self, vlan_manager: VlanManager):
        super().__init__(Vlan, AbstractVlan, vlan_manager)
        self.vlan_manager = vlan_manager

    @with_context
    @log_call
    def get_from_number(self, ctx, vlan_number):
        """ Get the state of a port """
        try:
            return self.vlan_manager.get_from_number(ctx, vlan_number).to_dict(), 200
        except Exception as e:
            return handle_error(ctx, e)
