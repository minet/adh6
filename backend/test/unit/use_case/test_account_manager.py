from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.entity.account import Account
from adh6.treasury.account_manager import AccountManager
from adh6.treasury.interfaces.account_repository import AccountRepository


@pytest.fixture
def anyio_backend():
    return "asyncio"


class TestGetCAV:
    @pytest.mark.anyio
    async def test_happy_path_no_cav(
        self,
        mock_account_repository: AccountRepository,
        account_manager: AccountManager,
    ):
        mock_account_repository.search_by = AsyncMock(return_value=([], 0))
        result = await account_manager.get_cav_balance()
        assert result == 0
        mock_account_repository.search_by.assert_awaited_once()

    @pytest.mark.anyio
    async def test_happy_path_cav(
        self,
        mock_account_repository: AccountRepository,
        account_manager: AccountManager,
        sample_account1: Account,
        sample_account2: Account,
    ):
        mock_account_repository.search_by = AsyncMock(
            return_value=([sample_account1, sample_account2], 2)
        )
        result = await account_manager.get_cav_balance()
        assert result == 0
        mock_account_repository.search_by.assert_awaited_once()


@pytest.fixture
def account_manager(mock_account_repository: AccountRepository):
    return AccountManager(mock_account_repository)


@pytest.fixture
def mock_account_repository():
    return MagicMock(spec=AccountRepository)
