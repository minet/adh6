from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.treasury.storage.account_repository import AccountSQLRepository
from adh6.treasury.storage.models import Account as SQLAccount


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.execute = AsyncMock()
    session.flush = AsyncMock()
    return session


@pytest.fixture
def account_repo(mock_session):
    return AccountSQLRepository(session=mock_session)


class TestAccountSQLRepository:
    async def test_get_by_id(self, account_repo, mock_session):
        # Given
        sql_acc = SQLAccount(
            id=1, name="Test", type=1, creation_date=None, adherent_id=None, compte_courant=True, pinned=False
        )
        mock_result = MagicMock()
        mock_result.one.return_value = (sql_acc, 100)  # (Account, balance)
        mock_session.execute.return_value = mock_result

        # When
        result = await account_repo.get_by_id(1)

        # Then
        assert result.id == 1
        assert result.balance == 100
        mock_session.execute.assert_called_once()

    async def test_search_by(self, account_repo, mock_session):
        # Given
        sql_acc = SQLAccount(
            id=1, name="Test", type=1, creation_date=None, adherent_id=None, compte_courant=True, pinned=False
        )
        mock_result = MagicMock()
        mock_result.all.return_value = [(sql_acc, 100)]
        mock_session.execute.return_value = mock_result

        # When
        results, count = await account_repo.search_by()

        # Then
        assert count == 1
        assert len(results) == 1
        assert results[0].balance == 100
