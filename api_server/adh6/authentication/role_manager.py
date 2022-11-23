from typing import List, Tuple, Union
from adh6.authentication import AuthenticationMethod, Roles
from adh6.authentication.interfaces import RoleRepository
from adh6.decorator import log_call
from adh6.entity import RoleMapping
from adh6.exceptions import MemberNotFoundError, NotFoundError, UpdateImpossible
from adh6.member import MemberManager


class RoleManager:
    def __init__(self, role_repository: RoleRepository, member_manager: MemberManager) -> None:
        self.role_repository = role_repository
        self.member_manager = member_manager

    @log_call
    def search(self, auth: str, identifier: Union[str, None] = None) -> Tuple[List[RoleMapping], int]:
        return self.role_repository.find(
            method=AuthenticationMethod(auth),
            identifiers=[identifier] if identifier else None,
        )

    @log_call
    def create(self, identifier: str, roles: List[str], auth: str = AuthenticationMethod.USER.value) -> None:
        method = AuthenticationMethod(auth)
        if method == AuthenticationMethod.API_KEY:
            raise UpdateImpossible("api key", "The roles for an api key cannot be changed. You might want to delete the key and recreate one")
        if method == AuthenticationMethod.USER:
            t = self.member_manager.get_by_login(login=identifier)
            if not t:
                raise MemberNotFoundError(identifier)
        self.role_repository.create(method=method, identifier=identifier, roles=[Roles(r) for r in roles])

    @log_call
    def delete(self, id: int) -> None:
        if not self.role_repository.get(id=id):
            raise NotFoundError("role mapping")
        self.role_repository.delete(id=id)
