from unittest.mock import MagicMock

import pytest
from adh6.entity import Vlan
from adh6.exceptions import VLANNotFoundError
from adh6.subnet.interfaces.vlan_repository import VlanRepository
from adh6.subnet.vlan_manager import VlanManager


class TestGetFromNumber:
    def test_happy_path(self,
                        sample_vlan: Vlan,
                        mock_vlan_repository: VlanRepository,
                        vlan_manager: VlanManager):
        mock_vlan_repository.get_vlan = MagicMock(return_value=(sample_vlan))

        assert sample_vlan == vlan_manager.get_from_number(sample_vlan.number)
        mock_vlan_repository.get_vlan.assert_called_once()

    def test_vlan_not_found(self,
                        sample_vlan: Vlan,
                        mock_vlan_repository: VlanRepository,
                        vlan_manager: VlanManager):
        mock_vlan_repository.get_vlan = MagicMock(return_value=(None), side_effect=VLANNotFoundError(""))

        with pytest.raises(VLANNotFoundError):
            vlan_manager.get_from_number(sample_vlan.number)

        mock_vlan_repository.get_vlan.assert_called_once()

@pytest.fixture
def mock_vlan_repository():
    return MagicMock(spec=VlanRepository)

@pytest.fixture
def vlan_manager(mock_vlan_repository: VlanRepository):
    yield VlanManager(mock_vlan_repository)
