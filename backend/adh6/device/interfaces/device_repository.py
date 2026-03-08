import abc

from adh6.default.crud_repository import CRUDRepository
from adh6.entity import AbstractDevice, Device, DeviceBody, DeviceFilter


class DeviceRepository(CRUDRepository[Device, AbstractDevice]):
    @abc.abstractmethod
    async def get_by_id(self, object_id: int) -> Device | None:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def create(self, obj: DeviceBody) -> Device:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def update(
        self, object_to_update: AbstractDevice, override: bool = False
    ) -> Device:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def delete(self, object_id: int):
        pass  # pragma: no cover

    @abc.abstractmethod
    async def search_by(
        self, limit: int, offset: int, device_filter: DeviceFilter
    ) -> tuple[list[Device], int]:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def get_by_mac(self, mac: str) -> Device | None:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def put_mab(self, id: int, mab: bool) -> bool:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def get_mab(self, id: int) -> bool:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def owner(self, id: int) -> int | None:
        pass  # pragma: no cover
