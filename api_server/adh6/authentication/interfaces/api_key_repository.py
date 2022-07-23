from abc import ABC, abstractmethod
from typing import List, Tuple, Union

from adh6.entity import ApiKey


class ApiKeyRepository(ABC):
    @abstractmethod
    def get(self, id: int) -> ApiKey:
        pass

    @abstractmethod
    def create(self, login: str) -> Tuple[int, str]:
        pass

    @abstractmethod
    def find(self, login: Union[str, None] = None, token_hash: Union[str, None] = None) -> List[ApiKey]:
        pass

    @abstractmethod
    def delete(self, id: int) -> None:
        pass
