import abc


class NetboxRepository(abc.ABC):
    @abc.abstractmethod
    async def assign_ip(self, ip_with_prefix: str, mac: str, member_id: int, nat_ip: str | None = None) -> None:
        """Create IP in Netbox. ip_with_prefix e.g. '10.0.0.5/24' or 'fe80::1/64'."""

    @abc.abstractmethod
    async def unassign_ip(self, ip_address: str) -> None:
        """Delete ADH6-tagged IP from Netbox by bare address."""

    @abc.abstractmethod
    async def create_wifi_prefix(self, prefix: str, member_id: int, nat_ip: str | None = None) -> None:
        """Create wifi private prefix + first-host gateway IP with ADH6 tag."""

    @abc.abstractmethod
    async def delete_wifi_prefix(self, prefix: str) -> None:
        """Delete all ADH6-tagged IPs in prefix, then delete prefix itself."""

    @abc.abstractmethod
    async def list_ips(self) -> list[str]:
        """Return bare IP addresses (no prefix len) of all ADH6-tagged IP entries."""

    @abc.abstractmethod
    async def list_prefixes(self) -> list[str]:
        """Return CIDR strings of all ADH6-tagged prefix entries."""
