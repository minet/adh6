import abc
from typing import List, Tuple, Union

from adh6.authentication import AuthenticationMethod, Roles
from adh6.entity import RoleMapping


class RoleRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, id: int) -> Union[RoleMapping, None]:
        pass

    @abc.abstractmethod
    def create(self, method: AuthenticationMethod, identifier: str, roles: List[Roles]) -> None:
        pass

    @abc.abstractmethod
    def find(self, method: Union[AuthenticationMethod, None] = None, identifiers: Union[List[str], None] = None, roles: Union[List[Roles], None] = None) -> Tuple[List[RoleMapping], int]:
        pass

    @abc.abstractmethod
    def delete(self, id: int) -> None:
        pass
