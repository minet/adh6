from abc import ABC, abstractmethod
import typing as t

from adh6.entity import ApiKey


class ApiKeyRepository(ABC):
    @abstractmethod
    def get(self, id: int) -> t.Union[ApiKey, None]:
        pass  # pragma: no cover

    @abstractmethod
    def create(self, login: str) -> t.Tuple[int, str]:
        pass  # pragma: no cover

    @abstractmethod
    def find(self, login: t.Union[str, None] = None, token_hash: t.Union[str, None] = None) -> t.List[ApiKey]:
        pass  # pragma: no cover

    @abstractmethod
    def delete(self, id: int) -> None:
        pass  # pragma: no cover
