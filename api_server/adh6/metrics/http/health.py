from adh6.default.decorator.with_context import with_context
from adh6.metrics.health_manager import HealthManager
from adh6.misc.context import log_extra
from adh6.misc.log import LOG


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
