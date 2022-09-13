# coding=utf-8
from adh6.entity import AbstractPort, Port
from adh6.decorator import log_call, with_context
from adh6.default.http_handler import DefaultHandler
from adh6.misc import log_extra, LOG

from ..interfaces import SwitchNetworkManager
from ..port_manager import PortManager


class PortHandler(DefaultHandler):
    def __init__(self, port_manager: PortManager, switch_network_manager: SwitchNetworkManager):
        super().__init__(Port, AbstractPort, port_manager)
        self.switch_network_manager = switch_network_manager

    @with_context
    @log_call
    def state_get(self, ctx, id_):
        """ Get the state of a port """
        return self.switch_network_manager.get_port_status(ctx, port_id=id_) == "up", 200

    @with_context
    @log_call
    def state_put(self, ctx, id_):
        return self.switch_network_manager.update_port_status(ctx, port_id=id_) == "up", 200

    @with_context
    @log_call
    def vlan_get(self, ctx, id_):
        LOG.debug("http_port_vlan_get_called", extra=log_extra(ctx, id=id_))
        if (self.switch_network_manager.get_port_vlan(ctx, port_id=id_)) == "No Such Instance currently exists at this OID" :
            return 1, 200
        return int(self.switch_network_manager.get_port_vlan(ctx, port_id=id_)), 200

    @with_context
    @log_call
    def vlan_put(self, ctx, id_, body):
        LOG.debug("http_port_vlan_put_called", extra=log_extra(ctx, id=id_))
        if (self.switch_network_manager.get_port_vlan(ctx, port_id=id_)) == "No Such Instance currently exists at this OID" :
            return 1, 200
        self.switch_network_manager.update_port_vlan(ctx, port_id=id_, vlan=int(body))
        return int(body), 204

    @with_context
    @log_call
    def mab_get(self, ctx, id_):
        return self.switch_network_manager.get_port_mab(ctx, port_id=id_) == "true", 200

    @with_context
    @log_call
    def mab_put(self, ctx, id_):
        return self.switch_network_manager.update_port_mab(ctx, port_id=id_) == 'true', 200

    @with_context
    @log_call
    def auth_get(self, ctx, id_):
        return self.switch_network_manager.get_port_auth(ctx, port_id=id_) == "auto", 200

    @with_context
    @log_call
    def auth_put(self, ctx, id_):
        return self.switch_network_manager.update_port_auth(ctx, port_id=id_) == "auto", 200

    @with_context
    @log_call
    def use_get(self, ctx, id_):
        return self.switch_network_manager.get_port_use(ctx, port_id=id_), 200

    @with_context
    @log_call
    def alias_get(self, ctx, id_):
        return self.switch_network_manager.get_port_alias(ctx, port_id=id_), 200

    @with_context
    @log_call
    def speed_get(self, ctx, id_):
        return self.switch_network_manager.get_port_speed(ctx, port_id=id_), 200
