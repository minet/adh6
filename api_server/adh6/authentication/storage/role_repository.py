from typing import List, Tuple, Union

from sqlalchemy import select, insert
from sqlalchemy.sql import Select, Insert
from adh6.authentication import AuthenticationMethod, Roles
from adh6.authentication.storage.models import AuthenticationRoleMapping
from adh6.entity import RoleMapping
from adh6.authentication.interfaces import RoleRepository
from adh6.storage import db
from adh6.storage.sql.models import Adherent


class RoleSQLRepository(RoleRepository):
    def find(self, method: Union[AuthenticationMethod, None] = None, identifiers: Union[List[str], None] = None, roles: Union[List[Roles], None] = None) -> Tuple[List[RoleMapping], int]:
        all_roles: List[AuthenticationRoleMapping] = []
        smt: Select = select(AuthenticationRoleMapping)
        if method == AuthenticationMethod.OIDC and identifiers is not None and len(identifiers) == 1:
            pass
        if method is not None: 
            smt = smt.where(AuthenticationRoleMapping.authentication == method)
        if identifiers is not None:
            smt = smt.where(AuthenticationRoleMapping.identifier.in_(identifiers))
        if roles is not None:
            smt = smt.where(AuthenticationRoleMapping.role.in_(roles))
        all_roles.extend(db.session().execute(smt).all())
        return [self._map_to_role_mapping(i[0]) for i in set(all_roles)], len(all_roles)

    def create(self, method: AuthenticationMethod, identifier: str, role: Roles) -> None:
        smt: Insert = insert(AuthenticationRoleMapping).values(
            role=role,
            identifier=identifier,
            authentication=method
        )
        db.session().execute(smt)

    def delete(self, method: AuthenticationMethod, identifier: str) -> None:
        pass

    def user_id_from_username(self, login: str) -> int:
        return db.session.execute(select(Adherent.id).where((Adherent.login == login) | (Adherent.ldap_login == login))).scalar()
    
    def _map_to_role_mapping(self, role: AuthenticationRoleMapping) -> RoleMapping:
        return RoleMapping(
            identifier=role.identifier,
            role=role.role.value,
            authentication=role.authentication.value
        )
