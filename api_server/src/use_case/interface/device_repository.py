# coding=utf-8

from typing import List

from src.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity import Device, AbstractDevice
from src.use_case.interface.crud_repository import CRUDRepository


class DeviceRepository(CRUDRepository):
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None,
                  filter_: AbstractDevice = None) -> (List[Device], int):
        raise NotImplemented

    def create(self, ctx, object_to_create: Device) -> object:
        raise NotImplemented

    def update(self, ctx, object_to_update: AbstractDevice, override=False) -> object:
        raise NotImplemented

    def delete(self, ctx, object_id) -> None:
        raise NotImplemented
