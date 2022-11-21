# coding=utf-8
from adh6.entity import AbstractVlan, Vlan
from adh6.decorator import log_call, with_context
from adh6.default.http_handler import DefaultHandler

from ..vlan_manager import VlanManager


class VLANHandler(DefaultHandler):
    def __init__(self, vlan_manager: VlanManager):
        super().__init__(Vlan, AbstractVlan, vlan_manager)
        self.vlan_manager = vlan_manager

    @with_context
    @log_call
    def get_from_number(self, ctx, vlan_number):
        """ Get the state of a port """
        return self.vlan_manager.get_from_number(ctx, vlan_number).to_dict(), 200
