# coding=utf-8
"""
Switch network manager interface.
"""
import abc

class SwitchNetworkManager(abc.ABC):
    """
    Abstract interface to manipulate the members.
    """

    @abc.abstractmethod
    def get_port_status(self, ctx, port_id: int) -> bool:
        """
        Retrieve the status of a port.

        :raise PortNotFound
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def update_port_status(self, ctx, port_id: int) -> str:
        """
        Update the status of a port.

        :raise PortNotFound
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_port_auth(self, ctx, port_id: int) -> bool:
        """
        Retrieve the status of a port.

        :raise PortNotFound
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def update_port_auth(self, ctx, port_id: int) -> str:
        """
        Update the status of a port.

        :raise PortNotFound
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_port_vlan(self, ctx, port_id: int) -> int:
        """
        Get the VLAN assigned to a port.

        :raise PortNotFound
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def update_port_vlan(self, ctx, port_id: int, vlan: int=1) -> str:
        """
        Update the VLAN assigned to a port.

        :raise PortNotFound
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_port_mab(self, ctx, port_id: int) -> bool:
        """
        Retrieve whether MAB is active on a port.

        :raise PortNotFound
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def update_port_mab(self, ctx, port_id: int) -> str:
        """
        Update whether MAB should be active on a port.

        :raise PortNotFound
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_port_use(self, ctx, port_id: int) -> bool:
        """
        Get the usage of a port.

        :raise PortNotFound
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_port_alias(self, ctx, port_id: int) -> str:
        """
        Get the alias of a port.

        :raise PortNotFound
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_port_speed(self, ctx, port_id: int) -> int:
        """
        Get the speed of a port.

        :raise PortNotFound
        """
        pass  # pragma: no cover
