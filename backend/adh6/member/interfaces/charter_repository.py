import abc
from datetime import datetime


class CharterRepository(abc.ABC):
    @abc.abstractmethod
    async def get(self, charter_id: int, member_id: int) -> datetime | None:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def get_members(self, charter_id: int) -> tuple[list[int], int]:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def update(self, charter_id: int, member_id: int) -> None:
        pass  # pragma: no cover
