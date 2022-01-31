# coding=utf-8
from src.entity import AbstractAccount
from src.entity.roles import Roles
from src.use_case.decorator.security import SecurityDefinition, defines_security, uses_security
from src.use_case.interface.logs_repository import LogsRepository


@defines_security(SecurityDefinition(
    item={
        "read": Roles.USER
    },
    collection={
        "read": Roles.USER
    }
))
class StatsManager:
    def __init__(self, logs_repository: LogsRepository):
        self.logs_repository = logs_repository

    @uses_security("read", is_collection=False)
    def get_global_stats(self, ctx):
        return self.logs_repository.get_global_stats(ctx)
