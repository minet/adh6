from adh6.decorator import with_context
from ..health_manager import HealthManager


class HealthHandler:
    def __init__(self, health_manager: HealthManager):
        self.health_manager = health_manager

    @with_context
    def health(self):
        if self.health_manager.is_healthy():
            return "OK", 200
        else:
            return "FAILURE", 503
