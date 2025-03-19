import abc
from typing import List, Tuple, Union

from adh6.authentication import AuthenticationMethod, Roles
from adh6.entity import RoleMapping


class RoleRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, id: int) -> RoleMapping | None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def create(self, method: AuthenticationMethod, identifier: str, roles: List[Roles]) -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def find(
        self,
        method: AuthenticationMethod | None = None,
        identifiers: List[str] | None = None,
        roles: List[Roles] | None = None,
    ) -> Tuple[List[RoleMapping], int]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def delete(self, id: int) -> None:
        pass  # pragma: no cover
