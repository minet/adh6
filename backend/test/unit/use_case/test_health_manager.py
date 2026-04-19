from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.metrics.health_manager import HealthManager
from adh6.metrics.interfaces.ping_repository import PingRepository


@pytest.fixture
def mock_ping_repository():
    return MagicMock(spec=PingRepository)


@pytest.fixture
def health_manager(mock_ping_repository):
    return HealthManager(ping_repository=mock_ping_repository)


class TestIsHealthy:
    async def test_healthy(self, health_manager, mock_ping_repository):
        # Given
        mock_ping_repository.ping = AsyncMock(return_value=True)

        # When
        result = await health_manager.is_healthy()

        # Then
        assert result is True
        mock_ping_repository.ping.assert_called_once()

    async def test_unhealthy(self, health_manager, mock_ping_repository):
        # Given
        mock_ping_repository.ping = AsyncMock(return_value=False)

        # When
        result = await health_manager.is_healthy()

        # Then
        assert result is False
        mock_ping_repository.ping.assert_called_once()
