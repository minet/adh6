import logging

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
