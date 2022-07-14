import abc
from typing import List

from adh6.authentication import AuthenticationMethod, Roles


class RoleRepository(abc.ABC):
    @abc.abstractmethod
    def get_roles(self, method: AuthenticationMethod = AuthenticationMethod.NONE, roles: List[str] = []) -> List[Roles]:
        pass

    @abc.abstractmethod
    def get_api_key_user(self, api_key: str) -> str:
        pass

    @abc.abstractmethod
    def get_user_id(self, user_name: str) -> int:
        pass
