from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.entity import AbstractVlan, Vlan, VlanStats
from adh6.exceptions import VLANNotFoundError
from adh6.subnet.interfaces.vlan_repository import VlanRepository
from adh6.subnet.vlan_manager import VlanManager


class TestGetFromNumber:
    async def test_happy_path(self, sample_vlan: Vlan, mock_vlan_repository: VlanRepository, vlan_manager: VlanManager):
        mock_vlan_repository.get_vlan = AsyncMock(return_value=(sample_vlan))
        assert sample_vlan.number is not None

        assert sample_vlan == await vlan_manager.get_from_number(sample_vlan.number)
        mock_vlan_repository.get_vlan.assert_called_once()

    async def test_vlan_not_found(
        self, sample_vlan: Vlan, mock_vlan_repository: VlanRepository, vlan_manager: VlanManager
    ):
        mock_vlan_repository.get_vlan = AsyncMock(return_value=(None), side_effect=VLANNotFoundError(""))
        assert sample_vlan.number is not None

        with pytest.raises(VLANNotFoundError):
            await vlan_manager.get_from_number(sample_vlan.number)

        mock_vlan_repository.get_vlan.assert_called_once()


class TestListVlans:
    async def test_returns_all_vlans(
        self, sample_vlan: Vlan, mock_vlan_repository: VlanRepository, vlan_manager: VlanManager
    ):
        expected = [AbstractVlan(id=sample_vlan.id, number=sample_vlan.number)]
        mock_vlan_repository.list_vlans = AsyncMock(return_value=expected)

        result = await vlan_manager.list_vlans()

        assert result == expected
        mock_vlan_repository.list_vlans.assert_called_once_with()

    async def test_returns_empty_list_when_no_vlans(
        self, mock_vlan_repository: VlanRepository, vlan_manager: VlanManager
    ):
        mock_vlan_repository.list_vlans = AsyncMock(return_value=[])

        result = await vlan_manager.list_vlans()

        assert result == []


class TestGetStats:
    async def test_returns_stats(
        self, sample_vlan: Vlan, mock_vlan_repository: VlanRepository, vlan_manager: VlanManager
    ):
        expected = [
            VlanStats(
                id=sample_vlan.id,
                number=sample_vlan.number,
                ipv4Network="157.159.41.0/24",
                ipv6Network=None,
                deviceCount=3,
                capacity=254,
                overLimitDevices=[],
            )
        ]
        mock_vlan_repository.get_stats = AsyncMock(return_value=expected)

        result = await vlan_manager.get_stats()

        assert result == expected
        mock_vlan_repository.get_stats.assert_called_once_with()

    async def test_returns_empty_when_no_vlans(self, mock_vlan_repository: VlanRepository, vlan_manager: VlanManager):
        mock_vlan_repository.get_stats = AsyncMock(return_value=[])

        result = await vlan_manager.get_stats()

        assert result == []


@pytest.fixture
def mock_vlan_repository():
    return MagicMock(spec=VlanRepository)


@pytest.fixture
def vlan_manager(mock_vlan_repository: VlanRepository):
    yield VlanManager(mock_vlan_repository)
