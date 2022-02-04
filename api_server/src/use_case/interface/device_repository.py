# coding=utf-8

from typing import List, Tuple

from src.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity import Device, AbstractDevice
from src.use_case.interface.crud_repository import CRUDRepository


class DeviceRepository(CRUDRepository):
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None,
                  filter_: AbstractDevice = None) -> Tuple[List[Device], int]:
        raise NotImplementedError

    def create(self, ctx, object_to_create: Device) -> object:
        raise NotImplementedError

    def update(self, ctx, object_to_update: AbstractDevice, override=False) -> object:
        raise NotImplementedError

    def delete(self, ctx, object_id) -> None:
        raise NotImplementedError

    def get_ip_address(self, ctx, type: str, filter_: AbstractDevice = None) -> Tuple[List[str], int]:
        raise NotImplementedError
