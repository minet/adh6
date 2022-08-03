from typing import List, Tuple, Union

from sqlalchemy import select, insert, delete
from sqlalchemy.sql import Select, Insert
from adh6.authentication import AuthenticationMethod, Roles
from adh6.authentication.storage.models import AuthenticationRoleMapping
from adh6.entity import RoleMapping
from adh6.authentication.interfaces import RoleRepository
from adh6.storage import db
from adh6.storage.sql.models import Adherent


class RoleSQLRepository(RoleRepository):
    def get(self, id: int) -> Union[RoleMapping, None]:
        smt: Select = select(AuthenticationRoleMapping).where(AuthenticationRoleMapping.id == id)
        return db.session().execute(smt).one_or_none()

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

    def create(self, method: AuthenticationMethod, identifier: str, roles: List[Roles]) -> None:
        smt: Insert = insert(AuthenticationRoleMapping).values(
            [
                {
                    'identifier': identifier,
                    'authentication': method,
                    'role': r
                } for r in roles
            ]
        )
        db.session().execute(smt)

    def delete(self, id: int) -> None:
        smt = delete(AuthenticationRoleMapping).where(AuthenticationRoleMapping.id == id)
        db.session.execute(smt)

    def user_id_from_username(self, login: str) -> int:
        return db.session.execute(select(Adherent.id).where((Adherent.login == login) | (Adherent.ldap_login == login))).scalar()
    
    def _map_to_role_mapping(self, role: AuthenticationRoleMapping) -> RoleMapping:
        return RoleMapping(
            id=role.id,
            identifier=role.identifier,
            role=role.role.value,
            authentication=role.authentication.value
        )
