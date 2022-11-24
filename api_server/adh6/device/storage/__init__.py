from .device_repository import DeviceSQLRepository as DeviceRepository
from .ip_allocator import IPSQLAllocator as IPAllocator
from .logs_repository import ElasticsearchLogsRepository as LogsRepository

from enum import Enum

class DeviceType(Enum):
    wired = 0
    wireless = 1

__all__ = ["DeviceRepository", "IPAllocator", "LogsRepository"]
