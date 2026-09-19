"""
Switch network manager interface.
"""

import abc
from collections.abc import Callable
from typing import TypedDict


class BulkOperationData(TypedDict):
    success: int
    failed: int
    errors: list[str]


class DiscoveredPortData(TypedDict):
    portNumber: str
    oid: str


class PingResultData(TypedDict):
    sent: int
    received: int
    minRtt: int
    avgRtt: int
    maxRtt: int


class SwitchNetworkManager(abc.ABC):
    """
    Abstract interface to manipulate the members.
    """

    @abc.abstractmethod
    async def get_port_status(self, port_id: int) -> str:
        """
        Retrieve the status of a port.

        :raise PortNotFound
        """
        # pragma: no cover

    @abc.abstractmethod
    async def update_port_status(self, port_id: int) -> str:
        """
        Update the status of a port.

        :raise PortNotFound
        """
        # pragma: no cover

    @abc.abstractmethod
    async def get_port_auth(self, port_id: int) -> str:
        """
        Retrieve the status of a port.

        :raise PortNotFound
        """
        # pragma: no cover

    @abc.abstractmethod
    async def update_port_auth(self, port_id: int) -> str:
        """
        Update the status of a port.

        :raise PortNotFound
        """
        # pragma: no cover

    @abc.abstractmethod
    async def get_port_vlan(self, port_id: int) -> str:
        """
        Get the VLAN assigned to a port.

        :raise PortNotFound
        """
        # pragma: no cover

    @abc.abstractmethod
    async def update_port_vlan(self, port_id: int, elevated: Callable[[], object], vlan: int = 1) -> str:
        """
        Update the VLAN assigned to a port.

        :raise PortNotFound
        """
        # pragma: no cover

    @abc.abstractmethod
    async def get_port_mab(self, port_id: int) -> str:
        """
        Retrieve whether MAB is active on a port.

        :raise PortNotFound
        """
        # pragma: no cover

    @abc.abstractmethod
    async def update_port_mab(self, port_id: int) -> str:
        """
        Update whether MAB should be active on a port.

        :raise PortNotFound
        """
        # pragma: no cover

    @abc.abstractmethod
    async def get_port_mini_router(self, port_id: int) -> bool:
        """
        Retrieve whether the Mini-Routeur preset is active on a port.

        :raise PortNotFound
        """
        # pragma: no cover

    @abc.abstractmethod
    async def update_port_mini_router(self, port_id: int, enabled: bool) -> None:
        """
        Apply or remove the Mini-Routeur preset on a port.

        :raise PortNotFound
        """
        # pragma: no cover

    @abc.abstractmethod
    async def get_port_use(self, port_id: int) -> str:
        """
        Get the usage of a port.

        :raise PortNotFound
        """
        # pragma: no cover

    @abc.abstractmethod
    async def get_port_alias(self, port_id: int) -> str:
        """
        Get the alias of a port.

        :raise PortNotFound
        """
        # pragma: no cover

    @abc.abstractmethod
    async def get_port_speed(self, port_id: int) -> str:
        """
        Get the speed of a port.

        :raise PortNotFound
        """
        # pragma: no cover

    @abc.abstractmethod
    async def update_port_alias(self, port_id: int, alias: str) -> str:
        """
        Set the description/alias of a port via IF-MIB::ifAlias.

        :raise PortNotFound
        """
        # pragma: no cover

    @abc.abstractmethod
    async def discover_ports(self, switch_id: int) -> list[DiscoveredPortData]:
        """
        Discover ports on a switch via SNMP.
        Returns a list of dicts with 'portNumber' and 'oid'.

        :raise SwitchNotFound
        :raise NetworkManagerReadError
        """
        # pragma: no cover

    @abc.abstractmethod
    async def sync_port_names(self, switch_id: int) -> BulkOperationData:
        """
        Sync port names from switch technical names (ifDescr) via SNMP.
        Updates the database.

        :raise SwitchNotFound
        :raise NetworkManagerReadError
        """
        # pragma: no cover

    @abc.abstractmethod
    async def ping_from_switch(
        self, switch_id: int, address: str, count: int = 5, timeout_ms: int = 2000, size: int = 100
    ) -> PingResultData:
        """
        Run an ICMP ping from the switch via Cisco SNMP Ping MIB (CISCO-PING-MIB).

        :raise SwitchNotFound
        :raise NetworkManagerReadError
        """
        # pragma: no cover
