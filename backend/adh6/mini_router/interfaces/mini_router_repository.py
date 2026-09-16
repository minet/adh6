import abc

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity import MiniRouter, MiniRouterLoan


class MiniRouterRepository(abc.ABC):
    @abc.abstractmethod
    async def search_by(
        self,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        terms: str | None = None,
        loaned: bool | None = None,
        overdue: bool | None = None,
    ) -> tuple[list[MiniRouter], int]:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def get_by_id(self, object_id: int) -> MiniRouter | None:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def is_taken(self, field: str, value: str, exclude_id: int | None = None) -> bool:
        """Whether another mini-router already uses this value for a unique field."""
        # pragma: no cover

    @abc.abstractmethod
    async def create(self, mini_router: MiniRouter) -> MiniRouter:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def update(self, object_id: int, mini_router: MiniRouter) -> MiniRouter:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def delete(self, object_id: int) -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def list_loans(self, mini_router_id: int | None = None, member_id: int | None = None) -> list[MiniRouterLoan]:
        """List loans, most recent first, filtered by mini-router and/or member."""
        # pragma: no cover

    @abc.abstractmethod
    async def get_loan(self, loan_id: int) -> MiniRouterLoan | None:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def create_loan(self, mini_router_id: int, loan: MiniRouterLoan, author_id: int) -> MiniRouterLoan:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def update_loan(self, loan_id: int, loan: MiniRouterLoan) -> MiniRouterLoan:
        pass  # pragma: no cover
