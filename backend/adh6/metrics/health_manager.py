import asyncio
import logging
import time
from collections.abc import Callable

from .interfaces.ping_repository import PingRepository


class HealthManager:
    """
    Response to health requests.
    """

    def __init__(self, ping_repository: PingRepository):
        self.health_repository = ping_repository

    async def is_healthy(self) -> bool:
        db_health = await self.health_repository.ping()
        if not db_health:
            logging.error("health_check_db_not_healthy")  # noqa: LOG015  # TODO: use scoped logger ?
            return False

        # TODO: add more health checks?

        logging.debug("health_check_success")  # noqa: LOG015  # TODO: use scoped logger ?
        return True


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
                    logging.warning("health_check_timeout")  # noqa: LOG015
                    self._healthy = False
                self._checked_at = self._clock()
            return self._healthy
