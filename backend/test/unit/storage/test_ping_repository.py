from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.metrics.storage.ping_repository import PingSQLRepository


@pytest.fixture
def mock_session():
    return MagicMock()


@pytest.fixture
def ping_repository(mock_session):
    return PingSQLRepository(session=mock_session)


class TestPingSQLRepository:
    async def test_ping_returns_true_when_database_answers(self, ping_repository, mock_session):
        result = MagicMock()
        result.scalar_one.return_value = 1
        mock_session.execute = AsyncMock(return_value=result)

        assert await ping_repository.ping() is True
        mock_session.execute.assert_awaited_once()
        result.scalar_one.assert_called_once_with()

    async def test_ping_returns_false_for_unexpected_result(self, ping_repository, mock_session):
        result = MagicMock()
        result.scalar_one.return_value = 0
        mock_session.execute = AsyncMock(return_value=result)

        assert await ping_repository.ping() is False

    async def test_ping_propagates_database_exception(self, ping_repository, mock_session):
        mock_session.execute = AsyncMock(side_effect=RuntimeError("database unavailable"))

        with pytest.raises(RuntimeError, match="database unavailable"):
            await ping_repository.ping()
