from .interfaces.ping_repository import PingRepository
from adh6.misc import log_extra, LOG


class HealthManager:
    """
    Response to health requests.
    """

    def __init__(self, ping_repository: PingRepository):
        self.health_repository = ping_repository

    def is_healthy(self, ctx) -> bool:
        db_health = self.health_repository.ping(ctx)
        if not db_health:
            LOG.error("health_check_db_not_healthy", extra=log_extra(ctx))
            return False

        # TODO: add more health checks?

        LOG.info("health_check_success", extra=log_extra(ctx))
        return True
