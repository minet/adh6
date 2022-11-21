import typing as t

from adh6.entity import DeviceFilter, Member
from adh6.decorator import log_call

from .interfaces import DeviceRepository, LogsRepository

class DeviceLogsManager:
    def __init__(self, device_repository: DeviceRepository, logs_repository: LogsRepository) -> None:
        self.logs_repository = logs_repository
        self.device_repository = device_repository
    
    @log_call
    def get(self, member: Member, dhcp: bool = False):
        devices, _ = self.device_repository.search_by(limit=20, offset=0, device_filter=DeviceFilter(member=member.id))
        return self.logs_repository.get(member=member, devices=devices, dhcp=dhcp)