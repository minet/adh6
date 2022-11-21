from .interfaces.ping_repository import PingRepository
import logging


class HealthManager:
    """
    Response to health requests.
    """

    def __init__(self, ping_repository: PingRepository):
        self.health_repository = ping_repository

    def is_healthy(self) -> bool:
        db_health = self.health_repository.ping()
        if not db_health:
            logging.error("health_check_db_not_healthy")
            return False

        # TODO: add more health checks?

        logging.debug("health_check_success")
        return True
