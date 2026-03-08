from __future__ import annotations

import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from adh6.authentication import AuthenticationMethod, Roles
    from adh6.entity import RoleMapping


class RoleRepository(abc.ABC):
    @abc.abstractmethod
    async def get(self, id: int) -> RoleMapping | None:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def create(
        self, method: AuthenticationMethod, identifier: str, roles: list[Roles]
    ) -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def find(
        self,
        method: AuthenticationMethod | None = None,
        identifiers: list[str] | None = None,
        roles: list[Roles] | None = None,
    ) -> tuple[list[RoleMapping], int]:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def delete(self, id: int) -> None:
        pass  # pragma: no cover
