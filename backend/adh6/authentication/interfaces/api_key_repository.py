from abc import ABC, abstractmethod

from adh6.entity import ApiKey


class ApiKeyRepository(ABC):
    @abstractmethod
    async def get(self, id: int) -> ApiKey | None:
        pass  # pragma: no cover

    @abstractmethod
    async def create(self, login: str) -> tuple[int, str]:
        pass  # pragma: no cover

    @abstractmethod
    async def find(self, login: str | None = None, token_hash: str | None = None) -> list[ApiKey]:
        pass  # pragma: no cover

    @abstractmethod
    async def delete(self, id: int) -> None:
        pass  # pragma: no cover
