# coding=utf-8
from connexion import NoContent

from adh6.entity import AbstractPort, Port
from adh6.exceptions import PortNotFoundError, SwitchNotFoundError
from adh6.default.decorator.log_call import log_call
from adh6.default.decorator.with_context import with_context
from adh6.default.http_handler import DefaultHandler
from adh6.network.interfaces.switch_network_manager import SwitchNetworkManager
from adh6.network.port_manager import PortManager
from adh6.misc.context import log_extra
from adh6.misc.log import LOG
from adh6.default.util.error import handle_error


class PortHandler(DefaultHandler):
    def __init__(self, port_manager: PortManager, switch_network_manager: SwitchNetworkManager):
        super().__init__(Port, AbstractPort, port_manager)
        self.switch_network_manager = switch_network_manager

    @with_context
    @log_call
    def state_get(self, ctx, id_):
        """ Get the state of a port """
        try:
            return self.switch_network_manager.get_port_status(ctx, port_id=id_) == "up", 200
        except SwitchNotFoundError:
            return NoContent, 404
        except PortNotFoundError:
            return NoContent, 404

    @with_context
    @log_call
    def state_put(self, ctx, id_):
        try:
            return self.switch_network_manager.update_port_status(ctx, port_id=id_) == "up", 200
        except SwitchNotFoundError:
            return NoContent, 404
        except PortNotFoundError:
            return NoContent, 404

    @with_context
    @log_call
    def vlan_get(self, ctx, id_):
        LOG.debug("http_port_vlan_get_called", extra=log_extra(ctx, id=id_))
        try:
            if (self.switch_network_manager.get_port_vlan(ctx, port_id=id_)) == "No Such Instance currently exists at this OID" :
                return 1, 200
            return int(self.switch_network_manager.get_port_vlan(ctx, port_id=id_)), 200
        except SwitchNotFoundError:
            return NoContent, 404
        except PortNotFoundError:
            return NoContent, 404

    @with_context
    @log_call
    def vlan_put(self, ctx, id_, body):
        LOG.debug("http_port_vlan_put_called", extra=log_extra(ctx, id=id_))
        try:
            if (self.switch_network_manager.get_port_vlan(ctx, port_id=id_)) == "No Such Instance currently exists at this OID" :
                return 1, 200
            self.switch_network_manager.update_port_vlan(ctx, port_id=id_, vlan=int(body))
            return int(body), 204
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def mab_get(self, ctx, id_):
        try:
            return self.switch_network_manager.get_port_mab(ctx, port_id=id_) == "true", 200
        except SwitchNotFoundError:
            return NoContent, 404
        except PortNotFoundError:
            return NoContent, 404

    @with_context
    @log_call
    def mab_put(self, ctx, id_):
        try:
            return self.switch_network_manager.update_port_mab(ctx, port_id=id_) == 'true', 200
        except SwitchNotFoundError:
            return NoContent, 404
        except PortNotFoundError:
            return NoContent, 404

    @with_context
    @log_call
    def auth_get(self, ctx, id_):
        try:
            return self.switch_network_manager.get_port_auth(ctx, port_id=id_) == "auto", 200
        except SwitchNotFoundError:
            return NoContent, 404
        except PortNotFoundError:
            return NoContent, 404

    @with_context
    @log_call
    def auth_put(self, ctx, id_):
        try:
            return self.switch_network_manager.update_port_auth(ctx, port_id=id_) == "auto", 200
        except SwitchNotFoundError:
            return NoContent, 404
        except PortNotFoundError:
            return NoContent, 404

    @with_context
    @log_call
    def use_get(self, ctx, id_):
        try:
            return self.switch_network_manager.get_port_use(ctx, port_id=id_), 200
        except SwitchNotFoundError:
            return NoContent, 404
        except PortNotFoundError:
            return NoContent, 404

    @with_context
    @log_call
    def alias_get(self, ctx, id_):
        try:
            return self.switch_network_manager.get_port_alias(ctx, port_id=id_), 200
        except SwitchNotFoundError:
            return NoContent, 404
        except PortNotFoundError:
            return NoContent, 404

    @with_context
    @log_call
    def speed_get(self, ctx, id_):
        try:
            return self.switch_network_manager.get_port_speed(ctx, port_id=id_), 200
        except SwitchNotFoundError:
            return NoContent, 404
        except PortNotFoundError:
            return NoContent, 404
