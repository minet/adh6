from typing import List, Tuple, Union
from adh6.authentication import AuthenticationMethod, Roles
from adh6.authentication.interfaces import ApiKeyRepository, RoleRepository
from adh6.default.decorator.auto_raise import auto_raise
from adh6.entity import ApiKey, AbstractMember
from adh6.exceptions import NotFoundError, ValidationError
from adh6.member.member_manager import MemberManager

class ApiKeyManager:
    def __init__(self, 
                 api_key_repository: ApiKeyRepository,
                 role_repository: RoleRepository,
                 member_manager: MemberManager):
        self.api_key_repository = api_key_repository
        self.role_repository = role_repository
        self.member_manager = member_manager

    @auto_raise
    def create(self, ctx, login: str, roles: List[str]) -> str:
        if len(roles) == 0:
            raise ValidationError()
        try:
            roles_ = [Roles(r) for r in roles]
        except:
            raise ValidationError()

        try:
            t, _ = self.member_manager.search(ctx, filter_=AbstractMember(username=login))
            if not t:
                raise NotFoundError("User not found")
        except Exception as e:
            raise e

        id_, value = self.api_key_repository.create(login=login)
        for r in roles_:
            self.role_repository.create(
                method=AuthenticationMethod.API_KEY,
                identifier=str(id_),
                role=r
            )
        return value

    def search(self, ctx, limit: int = 25, offset: int = 0, login: Union[str, None] = None) -> Tuple[List[ApiKey], int]:
        if login:
            try:
                t, _ = self.member_manager.search(ctx, filter_=AbstractMember(username=login))
                if not t:
                    raise NotFoundError("User not found")
            except Exception as e:
                raise e
        result = self.api_key_repository.find(login=login)
        return result, len(result)

    def delete(self, ctx, id: int):
        try:
            self.api_key_repository.get(id)
        except Exception as e:
            print(e)
            raise NotFoundError("ApiKey not found")
        self.api_key_repository.delete(id)
