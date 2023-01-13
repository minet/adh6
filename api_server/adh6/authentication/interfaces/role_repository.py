import abc
import typing as t

from adh6.authentication.enums import AuthenticationMethod, Roles
from adh6.entity import RoleMapping


class RoleRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, id: int) -> t.Union[RoleMapping, None]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def create(self, method: AuthenticationMethod, identifier: str, roles: t.List[Roles]) -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def find(self, method: t.Union[AuthenticationMethod, None] = None, identifiers: t.Union[t.List[str], None] = None, roles: t.Union[t.List[Roles], None] = None) -> t.Tuple[t.List[RoleMapping], int]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def delete(self, id: int) -> None:
        pass  # pragma: no cover
