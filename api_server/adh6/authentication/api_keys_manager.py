import typing as t
from adh6.entity import ApiKey
from adh6.exceptions import NotFoundError, ValidationError
from adh6.member import MemberManager

from . import AuthenticationMethod, Roles
from .interfaces import ApiKeyRepository, RoleRepository


class ApiKeyManager:
    def __init__(self, 
                 api_key_repository: ApiKeyRepository,
                 role_repository: RoleRepository,
                 member_manager: MemberManager):
        self.api_key_repository = api_key_repository
        self.role_repository = role_repository
        self.member_manager = member_manager

    def create(self, login: str, roles: t.List[str]) -> str:
        if len(roles) == 0:
            raise ValidationError()
        try:
            roles_ = [Roles(r) for r in roles]
        except:
            raise ValidationError()

        t = self.member_manager.get_by_login(login)
        if not t:
            raise NotFoundError("User not found")

        id_, value = self.api_key_repository.create(login=login)
        self.role_repository.create(
            method=AuthenticationMethod.API_KEY,
            identifier=str(id_),
            roles=roles_
        )
        return value

    def search(self, limit: int = 25, offset: int = 0, login: t.Union[str, None] = None) -> t.Tuple[t.List[ApiKey], int]:
        if login:
            t = self.member_manager.get_by_login(login)
            if not t:
                raise NotFoundError("User not found")
        result = self.api_key_repository.find(login=login)
        return result, len(result)

    def delete(self, id: int):
        if not self.api_key_repository.get(id):
            raise NotFoundError("ApiKey not foud")
        self.api_key_repository.delete(id)
