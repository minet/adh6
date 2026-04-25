import abc

from adh6.entity import AbstractVlan, VlanStats


class VlanRepository(abc.ABC):
    """
    Abstract interface to handle VLANs.
    """

    @abc.abstractmethod
    async def get_vlan(self, vlan_number: int) -> AbstractVlan:
        """
        Get a VLAN.

        :raise VlanNotFound
        """
        # pragma: no cover

    @abc.abstractmethod
    async def list_vlans(self) -> list[AbstractVlan]:
        """Return all VLANs."""
        # pragma: no cover

    @abc.abstractmethod
    async def get_stats(self) -> list[VlanStats]:
        """Return all VLANs with device counts and over-limit devices."""
        # pragma: no cover
