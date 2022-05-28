from unittest.mock import MagicMock

import pytest
from src.entity import Vlan
from src.exceptions import VLANNotFoundError
from src.use_case.interface.vlan_repository import VlanRepository
from src.use_case.vlan_manager import VlanManager


class TestGetFromNumber:
    def test_happy_path(self,
                        ctx,
                        sample_vlan: Vlan,
                        mock_vlan_repository: VlanRepository,
                        vlan_manager: VlanManager):
        mock_vlan_repository.get_vlan = MagicMock(return_value=(sample_vlan))

        assert sample_vlan == vlan_manager.get_from_number(ctx, sample_vlan.number)
        mock_vlan_repository.get_vlan.assert_called_once()

    def test_vlan_not_found(self,
                        ctx,
                        sample_vlan: Vlan,
                        mock_vlan_repository: VlanRepository,
                        vlan_manager: VlanManager):
        mock_vlan_repository.get_vlan = MagicMock(return_value=(None), side_effect=VLANNotFoundError(""))

        with pytest.raises(VLANNotFoundError):
            vlan_manager.get_from_number(ctx, sample_vlan.number)

        mock_vlan_repository.get_vlan.assert_called_once()

@pytest.fixture
def mock_vlan_repository():
    return MagicMock(spec=VlanRepository)

@pytest.fixture
def vlan_manager(mock_vlan_repository: VlanRepository):
    yield VlanManager(mock_vlan_repository)
