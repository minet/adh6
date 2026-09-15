import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.metrics.health_manager import HealthCache, HealthManager
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


class TestHealthCache:
    async def test_reuses_result_within_ttl(self, health_manager, mock_ping_repository):
        mock_ping_repository.ping = AsyncMock(return_value=True)
        now = [0.0]
        cache = HealthCache(ttl=5.0, clock=lambda: now[0])

        await cache.is_healthy(health_manager)
        now[0] = 4.9
        result = await cache.is_healthy(health_manager)

        assert result is True
        mock_ping_repository.ping.assert_called_once()

    async def test_refreshes_after_ttl(self, health_manager, mock_ping_repository):
        mock_ping_repository.ping = AsyncMock(side_effect=[True, False])
        now = [0.0]
        cache = HealthCache(ttl=5.0, clock=lambda: now[0])

        await cache.is_healthy(health_manager)
        now[0] = 5.0
        result = await cache.is_healthy(health_manager)

        assert result is False
        assert mock_ping_repository.ping.call_count == 2

    async def test_concurrent_calls_ping_once(self, health_manager, mock_ping_repository):
        mock_ping_repository.ping = AsyncMock(return_value=True)
        cache = HealthCache()

        results = await asyncio.gather(*(cache.is_healthy(health_manager) for _ in range(20)))

        assert all(results)
        mock_ping_repository.ping.assert_called_once()

    async def test_timeout_is_unhealthy(self, health_manager, mock_ping_repository):
        async def slow_ping():
            await asyncio.sleep(1)
            return True

        mock_ping_repository.ping = slow_ping
        cache = HealthCache(timeout=0.01)

        assert await cache.is_healthy(health_manager) is False
