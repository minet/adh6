from adh6.decorator import with_context
from adh6.misc import log_extra, LOG

from ..health_manager import HealthManager


class HealthHandler:
    def __init__(self, health_manager: HealthManager):
        self.health_manager = health_manager

    @with_context
    def health(self, ctx):
        LOG.debug("http_health_called", extra=log_extra(ctx))

        if self.health_manager.is_healthy(ctx):
            return "OK", 200
        else:
            return "FAILURE", 503
