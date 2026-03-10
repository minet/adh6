import abc

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity import AccountType


class AccountTypeRepository(abc.ABC):
    @abc.abstractmethod
    async def get_by_id(self, object_id: int) -> AccountType:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def search_by(
        self, limit: int = DEFAULT_LIMIT, offset: int = DEFAULT_OFFSET, terms: str | None = None
    ) -> tuple[list[AccountType], int]:
        pass  # pragma: no cover
