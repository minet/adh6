import abc
from datetime import datetime


class CharterRepository(abc.ABC):
    @abc.abstractmethod
    async def get(self, charter_id, member_id) -> datetime | None:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def get_members(self, charter_id) -> tuple[list[int], int]:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def update(self, charter_id, member_id) -> None:
        pass  # pragma: no cover
