from adh6.entity import ApiKey
from adh6.exceptions import NotFoundError, ValidationError
from adh6.member.member_manager import MemberManager

from . import AuthenticationMethod, Roles
from .interfaces import ApiKeyRepository, RoleRepository


class ApiKeyManager:
    def __init__(
        self,
        api_key_repository: ApiKeyRepository,
        role_repository: RoleRepository,
        member_manager: MemberManager,
    ):
        self.api_key_repository = api_key_repository
        self.role_repository = role_repository
        self.member_manager = member_manager

    async def create(self, login: str, roles: list[str]) -> str:
        if len(roles) == 0:
            raise ValidationError
        try:
            roles_ = [Roles(r) for r in roles]
        except Exception:
            raise ValidationError

        t = await self.member_manager.get_by_login(login)
        if not t:
            raise NotFoundError("User not found")

        id_, value = await self.api_key_repository.create(login=login)
        await self.role_repository.create(
            method=AuthenticationMethod.API_KEY, identifier=str(id_), roles=roles_
        )
        return value

    async def search(
        self, limit: int = 25, offset: int = 0, login: str | None = None
    ) -> tuple[list[ApiKey], int]:
        if login:
            t = await self.member_manager.get_by_login(login)
            if not t:
                raise NotFoundError("User not found")
        result = await self.api_key_repository.find(login=login)
        return result, len(result)

    async def delete(self, id: int):
        if not await self.api_key_repository.get(id):
            raise NotFoundError("ApiKey not foud")
        await self.api_key_repository.delete(id)
