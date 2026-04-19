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
    ):
        account1 = MagicMock(spec=Account)
        account1.balance = 100
        account2 = MagicMock(spec=Account)
        account2.balance = 200
        mock_account_repository.search_by = AsyncMock(return_value=([account1, account2], 2))
        result = await account_manager.get_cav_balance()
        assert result == 300
        mock_account_repository.search_by.assert_awaited_once()


@pytest.fixture
def account_manager(mock_account_repository: AccountRepository):
    return AccountManager(mock_account_repository)


@pytest.fixture
def mock_account_repository():
    return MagicMock(spec=AccountRepository)
