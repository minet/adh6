from __future__ import annotations

import abc
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from adh6.authentication.enums import Roles
    from adh6.entity import Naina


class NainaRepository(abc.ABC):
    @abc.abstractmethod
    async def create(self, identifier: str, roles: tuple[Roles, ...], expires_at: datetime) -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def find_active(self, now: datetime) -> list[Naina]:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def revoke(self, identifier: str) -> None:
        pass  # pragma: no cover
