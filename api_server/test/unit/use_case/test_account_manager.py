from unittest.mock import MagicMock

import pytest
from src.entity.account import Account
from src.use_case.account_manager import AccountManager
from src.use_case.interface.account_repository import AccountRepository


class TestGetCAV:
    def test_happy_path_no_cav(self, ctx,
                        mock_account_repository: AccountRepository,
                        account_manager: AccountManager):
        mock_account_repository.search_by = MagicMock(return_value=([], 0))
        r = account_manager.get_cav_balance(ctx)
        assert r == 0
        mock_account_repository.search_by.assert_called_once()
        
    def test_happy_path_cav(self, ctx,
                            mock_account_repository: AccountRepository,
                            account_manager: AccountManager,
                            sample_account1: Account,
                            sample_account2: Account):
        mock_account_repository.search_by = MagicMock(return_value=([sample_account1, sample_account2], 2))
        r = account_manager.get_cav_balance(ctx)
        assert r == 0
        mock_account_repository.search_by.assert_called_once()
        

@pytest.fixture
def account_manager(mock_account_repository: AccountRepository):
    return AccountManager(mock_account_repository)

@pytest.fixture
def mock_account_repository():
    return MagicMock(spec=AccountRepository)
