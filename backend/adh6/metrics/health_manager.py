import asyncio
import logging
import time
from collections.abc import Callable

from .interfaces.ping_repository import PingRepository

logger = logging.getLogger(__name__)


class HealthManager:
    """Check whether the application is ready to serve requests."""

    def __init__(self, ping_repository: PingRepository):
        self._ping_repository = ping_repository

    async def is_healthy(self) -> bool:
        try:
            is_database_healthy = await self._ping_repository.ping()
        except Exception:
            logger.exception("health_check_db_failed")
            return False

        if not is_database_healthy:
            logger.warning("health_check_db_not_healthy")

        return is_database_healthy


class HealthCache:
    """Shares one health check between all callers for `ttl` seconds, so a public endpoint can't flood the DB."""

    def __init__(self, ttl: float = 5.0, timeout: float = 3.0, clock: Callable[[], float] = time.monotonic):
        self.ttl = ttl
        self.timeout = timeout
        self._clock = clock
        self._lock = asyncio.Lock()
        self._checked_at: float | None = None
        self._healthy = False

    async def is_healthy(self, manager: HealthManager) -> bool:
        async with self._lock:
            if self._checked_at is None or self._clock() - self._checked_at >= self.ttl:
                try:
                    async with asyncio.timeout(self.timeout):
                        self._healthy = await manager.is_healthy()
                except TimeoutError:
                    logger.warning("health_check_timeout", extra={"timeout_seconds": self.timeout})
                    self._healthy = False
                except Exception:
                    logger.exception("health_check_failed")
                    self._healthy = False
                self._checked_at = self._clock()
            return self._healthy
