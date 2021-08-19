# coding=utf-8
from connexion import NoContent

from src.entity import AbstractPort, Port
from src.exceptions import PortNotFoundError, SwitchNotFoundError
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.http_api.default import DefaultHandler
from src.interface_adapter.sql.decorator.sql_session import require_sql
from src.use_case.interface.switch_network_manager import SwitchNetworkManager
from src.use_case.port_manager import PortManager
from src.use_case.switch_manager import SwitchManager
from src.util.context import log_extra
from src.util.log import LOG


class PortHandler(DefaultHandler):
    def __init__(self, port_manager: PortManager, switch_manager: SwitchManager,
                 switch_network_manager: SwitchNetworkManager):
        super().__init__(Port, AbstractPort, port_manager)
        self.port_manager = port_manager
        self.switch_manager = switch_manager
        self.switch_network_manager = switch_network_manager

    @with_context
    @require_sql
    @log_call
    def state_get(self, ctx, port_id):
        """ Get the state of a port """

        try:
            port = self.port_manager.get_by_id(ctx, port_id=port_id)
            switch = self.switch_manager.get_by_id(ctx, switch_id=port.switch_obj.id)

            return True if self.switch_network_manager.get_port_status(ctx, switch, port) == "up" else False, 200
        except SwitchNotFoundError:
            return NoContent, 404
        except PortNotFoundError:
            return NoContent, 404

    @with_context
    @require_sql
    @log_call
    def state_put(self, ctx, port_id, body):
        #return NoContent, 501
        try:
            port = self.port_manager.get_by_id(ctx, port_id=port_id)
            switch = self.switch_manager.get_by_id(ctx, switch_id=port.switch_obj.id)
            print("TEST DE FERMETURE DE PORT \n\n" + self.switch_network_manager.update_port_status(ctx, switch, port))
            return NoContent, 204
            #return True if self.switch_network_manager.update_port_mab(ctx, switch, port), 200
            #return self.switch_network_manager.get_port_mab(ctx, switch, port), 200
        except SwitchNotFoundError:
            return NoContent, 404
        except PortNotFoundError:
            return NoContent, 404

    @with_context
    @require_sql
    @log_call
    def vlan_get(self, ctx, port_id):
        LOG.debug("http_port_vlan_get_called", extra=log_extra(ctx, port_id=port_id))

        try:
            port = self.port_manager.get_by_id(ctx, port_id=port_id)
            switch = self.switch_manager.get_by_id(ctx, switch_id=port.switch_obj.id)
            print("LE VLAN : " + self.switch_network_manager.get_port_vlan(ctx, switch, port))
            if (self.switch_network_manager.get_port_vlan(ctx, switch, port)) == "No Such Instance currently exists at this OID" :
                return 1, 200

            return int(self.switch_network_manager.get_port_vlan(ctx, switch, port)), 200
        except SwitchNotFoundError:
            return NoContent, 404
        except PortNotFoundError:
            return NoContent, 404

    @with_context
    @require_sql
    @log_call
    def vlan_put(self, ctx, port_id, body):
        LOG.debug("http_port_vlan_put_called", extra=log_extra(ctx, port_id=port_id))

        try:
            print(port_id, body)
            port = self.port_manager.get_by_id(ctx, port_id=port_id)
            switch = self.switch_manager.get_by_id(ctx, switch_id=port.switch_obj.id)

            print("\n\n\n\n\n" + str(body))
            if (self.switch_network_manager.get_port_vlan(ctx, switch, port)) == "No Such Instance currently exists at this OID" :
                return 1, 200

            print("Update de VLAN : " + self.switch_network_manager.update_port_vlan(ctx, switch, port, int(body)))
            return int(body), 204
        except SwitchNotFoundError:
            return NoContent, 404
        except PortNotFoundError:
            return NoContent, 404

    @with_context
    @require_sql
    @log_call
    def mab_get(self, ctx, port_id):
        #LOG.debug("http_port_mab_get_called", extra=log_extra(ctx, port_id=port_id))

        try:
            port = self.port_manager.get_by_id(ctx, port_id=port_id)
            switch = self.switch_manager.get_by_id(ctx, switch_id=port.switch_obj.id)
            print("HAHUAHUA\n\n" + self.switch_network_manager.get_port_mab(ctx, switch, port))
            return True if self.switch_network_manager.get_port_mab(ctx, switch, port) == "true" else False, 200
            #return self.switch_network_manager.get_port_mab(ctx, switch, port), 200
        except SwitchNotFoundError:
            return NoContent, 404
        except PortNotFoundError:
            return NoContent, 404

    @with_context
    @require_sql
    @log_call
    def mab_put(self, ctx, port_id, body):
        #return NoContent, 501
        try:
            port = self.port_manager.get_by_id(ctx, port_id=port_id)
            switch = self.switch_manager.get_by_id(ctx, switch_id=port.switch_obj.id)
            print("TEST DE CHANGEMENT DE MAB\n\n" + self.switch_network_manager.update_port_mab(ctx, switch, port))
            return NoContent, 204
            #return True if self.switch_network_manager.update_port_mab(ctx, switch, port), 200
            #return self.switch_network_manager.get_port_mab(ctx, switch, port), 200
        except SwitchNotFoundError:
            return NoContent, 404
        except PortNotFoundError:
            return NoContent, 404

    @with_context
    @require_sql
    @log_call
    def auth_get(self, ctx, port_id):
        #LOG.debug("http_port_mab_get_called", extra=log_extra(ctx, port_id=port_id))

        try:
            port = self.port_manager.get_by_id(ctx, port_id=port_id)
            switch = self.switch_manager.get_by_id(ctx, switch_id=port.switch_obj.id)
            print("AUTHENTIFICATION\n\n" + self.switch_network_manager.get_port_auth(ctx, switch, port))
            return True if self.switch_network_manager.get_port_auth(ctx, switch, port) == "true" else False, 200
        except SwitchNotFoundError:
            return NoContent, 404
        except PortNotFoundError:
            return NoContent, 404

    @with_context
    @require_sql
    @log_call
    def auth_put(self, ctx, port_id):
        #LOG.debug("http_port_mab_get_called", extra=log_extra(ctx, port_id=port_id))

        try:
            port = self.port_manager.get_by_id(ctx, port_id=port_id)
            switch = self.switch_manager.get_by_id(ctx, switch_id=port.switch_obj.id)
            print("CHANGEMENT D'AUTHENTIFICATION\n\n" + self.switch_network_manager.update_port_auth(ctx, switch, port))
            return NoContent,204
        except SwitchNotFoundError:
            return NoContent, 404
        except PortNotFoundError:
            return NoContent, 404

    @with_context
    @require_sql
    @log_call
    def use_get(self, ctx, port_id):
        #LOG.debug("http_port_mab_get_called", extra=log_extra(ctx, port_id=port_id))

        try:
            port = self.port_manager.get_by_id(ctx, port_id=port_id)
            switch = self.switch_manager.get_by_id(ctx, switch_id=port.switch_obj.id)
            print("Y A QUELQU'UN ? \n\n" + self.switch_network_manager.get_port_use(ctx, switch, port))
            return True if self.switch_network_manager.get_port_use(ctx, switch, port) == "true" else False, 200
        except SwitchNotFoundError:
            return NoContent, 404
        except PortNotFoundError:
            return NoContent, 404

    @with_context
    @require_sql
    @log_call
    def alias_get(self, ctx, port_id):
        #LOG.debug("http_port_mab_get_called", extra=log_extra(ctx, port_id=port_id))

        try:
            port = self.port_manager.get_by_id(ctx, port_id=port_id)
            switch = self.switch_manager.get_by_id(ctx, switch_id=port.switch_obj.id)
            print("Y A QUELQU'UN ? \n\n" + self.switch_network_manager.get_port_alias(ctx, switch, port))
            return True if self.switch_network_manager.get_port_alias(ctx, switch, port) == "true" else False, 200
        except SwitchNotFoundError:
            return NoContent, 404
        except PortNotFoundError:
            return NoContent, 404

    @with_context
    @require_sql
    @log_call
    def speed_get(self, ctx, port_id):
        #LOG.debug("http_port_mab_get_called", extra=log_extra(ctx, port_id=port_id))

        try:
            port = self.port_manager.get_by_id(ctx, port_id=port_id)
            switch = self.switch_manager.get_by_id(ctx, switch_id=port.switch_obj.id)
            print("Y A QUELQU'UN ? \n\n" + self.switch_network_manager.get_port_speed(ctx, switch, port))
            return True if self.switch_network_manager.get_port_speed(ctx, switch, port) == "true" else False, 200
        except SwitchNotFoundError:
            return NoContent, 404
        except PortNotFoundError:
            return NoContent, 404