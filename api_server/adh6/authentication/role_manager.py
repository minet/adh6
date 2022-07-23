from typing import List, Tuple, Union
from adh6.authentication import AuthenticationMethod, Roles
from adh6.authentication.interfaces import RoleRepository
from adh6.entity import RoleMapping, AbstractMember
from adh6.exceptions import MemberNotFoundError, UpdateImpossible
from adh6.member.member_manager import MemberManager


class RoleManager:
    def __init__(self, role_repository: RoleRepository, member_manager: MemberManager) -> None:
        self.role_repository = role_repository
        self.member_manager = member_manager

    def search(self, ctx, filter_: Union[RoleMapping, None] = None) -> Tuple[List[str], int]:
        method, identifier, roles = None, None, None
        if filter_:
            method = AuthenticationMethod(filter_.authentication)
            identifier = filter_.identifier
            roles = [Roles(filter_.role)]

        result, count = self.role_repository.find(
            method=method,
            identifiers=identifier,
            roles=roles
        )
        return [r.role for r in result if r.role], count

    def create(self, ctx, identifier: str, role: str, method: AuthenticationMethod = AuthenticationMethod.USER) -> None:
        if method == AuthenticationMethod.API_KEY:
            raise UpdateImpossible("api key", "The roles for an api key cannot be changed. You might want to delete the key and recreate one")
        if method == AuthenticationMethod.USER:
            try:
                t, _ = self.member_manager.search(ctx=ctx, filter_=AbstractMember(username=identifier))
                if not t:
                    raise MemberNotFoundError()
            except Exception as e:
                raise e
        self.role_repository.create(method=method, identifier=identifier, role=Roles(role))

