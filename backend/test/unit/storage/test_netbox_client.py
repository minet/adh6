from unittest.mock import MagicMock

import pytest
from adh6.device.storage.netbox_client import PyNetboxRepository
from pytest import fixture


@fixture
def mock_nb():
    return MagicMock()


@fixture
def repo(mock_nb):
    r = PyNetboxRepository(url="http://netbox.test", token="tok", tag_slug="adh6", strict=False)
    r._nb = mock_nb
    return r


@fixture
def strict_repo(mock_nb):
    r = PyNetboxRepository(url="http://netbox.test", token="tok", tag_slug="adh6", strict=True)
    r._nb = mock_nb
    return r


class TestAssignIp:
    def test_creates_ip_address(self, repo: PyNetboxRepository, mock_nb: MagicMock):
        repo._sync_assign_ip("10.0.0.5/24", "AA-BB-CC-DD-EE-FF", 42)

        mock_nb.ipam.ip_addresses.create.assert_called_once_with(
            address="10.0.0.5/24",
            status="active",
            tags=[{"slug": "adh6"}],
            custom_fields={"adh6_mac": "AA-BB-CC-DD-EE-FF", "adh6_id": 42},
            nat_outside=[],
        )

    def test_creates_ip_with_nat(self, repo: PyNetboxRepository, mock_nb: MagicMock):
        fake_nat_ip = MagicMock(id=123)
        mock_nb.ipam.ip_addresses.get.return_value = fake_nat_ip

        repo._sync_assign_ip("10.0.0.5/24", "AA-BB-CC-DD-EE-FF", 42, nat_ip="1.2.3.4")

        mock_nb.ipam.ip_addresses.get.assert_called_once_with(address="1.2.3.4")
        mock_nb.ipam.ip_addresses.create.assert_called_once_with(
            address="10.0.0.5/24",
            status="active",
            tags=[{"slug": "adh6"}],
            custom_fields={"adh6_mac": "AA-BB-CC-DD-EE-FF", "adh6_id": 42},
            nat_outside=[123],
        )

    async def test_non_strict_swallows_error(self, repo: PyNetboxRepository, mock_nb: MagicMock):
        mock_nb.ipam.ip_addresses.create.side_effect = RuntimeError("unreachable")

        # Should not raise
        await repo.assign_ip("10.0.0.5/24", "AA-BB-CC-DD-EE-FF", 42)

    async def test_strict_reraises(self, strict_repo: PyNetboxRepository, mock_nb: MagicMock):
        mock_nb.ipam.ip_addresses.create.side_effect = RuntimeError("unreachable")

        with pytest.raises(RuntimeError, match="unreachable"):
            await strict_repo.assign_ip("10.0.0.5/24", "AA-BB-CC-DD-EE-FF", 42)


class TestUnassignIp:
    def test_deletes_existing_ip(self, repo: PyNetboxRepository, mock_nb: MagicMock):
        fake_ip = MagicMock()
        mock_nb.ipam.ip_addresses.get.return_value = fake_ip

        repo._sync_unassign_ip("10.0.0.5")

        mock_nb.ipam.ip_addresses.get.assert_called_once_with(address="10.0.0.5", tag="adh6")
        fake_ip.delete.assert_called_once()

    def test_noop_when_not_found(self, repo: PyNetboxRepository, mock_nb: MagicMock):
        mock_nb.ipam.ip_addresses.get.return_value = None

        repo._sync_unassign_ip("10.0.0.5")

        mock_nb.ipam.ip_addresses.get.assert_called_once()
        # No delete call since ip is None

    async def test_non_strict_swallows_error(self, repo: PyNetboxRepository, mock_nb: MagicMock):
        mock_nb.ipam.ip_addresses.get.side_effect = RuntimeError("unreachable")

        await repo.unassign_ip("10.0.0.5")

    async def test_strict_reraises(self, strict_repo: PyNetboxRepository, mock_nb: MagicMock):
        mock_nb.ipam.ip_addresses.get.side_effect = RuntimeError("unreachable")

        with pytest.raises(RuntimeError):
            await strict_repo.unassign_ip("10.0.0.5")


class TestCreateWifiPrefix:
    def test_creates_prefix_and_first_host_as_gateway(self, repo: PyNetboxRepository, mock_nb: MagicMock):
        repo._sync_create_wifi_prefix("192.168.42.0/28", 7)

        mock_nb.ipam.prefixes.create.assert_called_once_with(
            prefix="192.168.42.0/28",
            status="active",
            tags=[{"slug": "adh6"}],
            custom_fields={"adh6_id": 7},
        )
        # First host of 192.168.42.0/28 is 192.168.42.1
        mock_nb.ipam.ip_addresses.create.assert_called_once_with(
            address="192.168.42.1/28",
            status="active",
            tags=[{"slug": "adh6"}],
            custom_fields={"adh6_id": 7},
            nat_outside=[],
        )

    def test_creates_prefix_with_nat(self, repo: PyNetboxRepository, mock_nb: MagicMock):
        fake_nat_ip = MagicMock(id=123)
        mock_nb.ipam.ip_addresses.get.return_value = fake_nat_ip
        fake_gateway_ip = MagicMock(id=456)
        mock_nb.ipam.ip_addresses.create.return_value = fake_gateway_ip

        repo._sync_create_wifi_prefix("192.168.42.0/28", 7, nat_ip="1.2.3.4")

        mock_nb.ipam.prefixes.create.assert_called_once()
        mock_nb.ipam.ip_addresses.get.assert_called_once_with(address="1.2.3.4")
        mock_nb.ipam.ip_addresses.create.assert_called_once_with(
            address="192.168.42.1/28",
            description="gateway",
            status="active",
            tags=[{"slug": "adh6"}],
            custom_fields={"adh6_id": 7},
            nat_outside=[123],
        )
        fake_nat_ip.update.assert_called_once_with({"nat_inside": 456})

    async def test_non_strict_swallows_error(self, repo: PyNetboxRepository, mock_nb: MagicMock):
        mock_nb.ipam.prefixes.create.side_effect = RuntimeError("unreachable")

        await repo.create_wifi_prefix("192.168.42.0/28", 7)

    async def test_strict_reraises(self, strict_repo: PyNetboxRepository, mock_nb: MagicMock):
        mock_nb.ipam.prefixes.create.side_effect = RuntimeError("unreachable")

        with pytest.raises(RuntimeError):
            await strict_repo.create_wifi_prefix("192.168.42.0/28", 7)


class TestDeleteWifiPrefix:
    def test_deletes_ips_then_prefix(self, repo: PyNetboxRepository, mock_nb: MagicMock):
        ip1, ip2 = MagicMock(), MagicMock()
        mock_nb.ipam.ip_addresses.filter.return_value = [ip1, ip2]
        fake_prefix = MagicMock()
        mock_nb.ipam.prefixes.get.return_value = fake_prefix

        repo._sync_delete_wifi_prefix("192.168.42.0/28")

        mock_nb.ipam.ip_addresses.filter.assert_called_once_with(parent="192.168.42.0/28", tag="adh6")
        ip1.delete.assert_called_once()
        ip2.delete.assert_called_once()
        mock_nb.ipam.prefixes.get.assert_called_once_with(prefix="192.168.42.0/28", tag="adh6")
        fake_prefix.delete.assert_called_once()

    def test_skips_prefix_delete_when_not_found(self, repo: PyNetboxRepository, mock_nb: MagicMock):
        mock_nb.ipam.ip_addresses.filter.return_value = []
        mock_nb.ipam.prefixes.get.return_value = None

        repo._sync_delete_wifi_prefix("192.168.42.0/28")

    async def test_non_strict_swallows_error(self, repo: PyNetboxRepository, mock_nb: MagicMock):
        mock_nb.ipam.ip_addresses.filter.side_effect = RuntimeError("unreachable")

        await repo.delete_wifi_prefix("192.168.42.0/28")

    async def test_strict_reraises(self, strict_repo: PyNetboxRepository, mock_nb: MagicMock):
        mock_nb.ipam.ip_addresses.filter.side_effect = RuntimeError("unreachable")

        with pytest.raises(RuntimeError):
            await strict_repo.delete_wifi_prefix("192.168.42.0/28")
