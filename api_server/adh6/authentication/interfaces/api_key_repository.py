import typing as t
from abc import ABC, abstractmethod

from adh6.entity import ApiKey


class ApiKeyRepository(ABC):
    @abstractmethod
    def get(self, id: int) -> ApiKey | None:
        pass  # pragma: no cover

    @abstractmethod
    def create(self, login: str) -> t.Tuple[int, str]:
        pass  # pragma: no cover

    @abstractmethod
    def find(self, login: str | None = None, token_hash: str | None = None) -> t.List[ApiKey]:
        pass  # pragma: no cover

    @abstractmethod
    def delete(self, id: int) -> None:
        pass  # pragma: no cover
