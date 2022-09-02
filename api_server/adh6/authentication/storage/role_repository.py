from typing import List, Tuple, Union
from sqlalchemy.orm import Session

from sqlalchemy import select, insert, delete, update
from sqlalchemy.sql import Select, Insert
from adh6.authentication import AuthenticationMethod, Roles
from adh6.authentication.storage.models import AuthenticationRoleMapping
from adh6.entity import RoleMapping
from adh6.authentication.interfaces import RoleRepository
from adh6.storage import db
from adh6.member.storage.models import Adherent


class RoleSQLRepository(RoleRepository):
    def get(self, id: int) -> Union[RoleMapping, None]:
        smt: Select = select(AuthenticationRoleMapping).where(AuthenticationRoleMapping.id == id)
        return db.session().execute(smt).one_or_none()

    def find(self, method: Union[AuthenticationMethod, None] = None, identifiers: Union[List[str], None] = None, roles: Union[List[Roles], None] = None) -> Tuple[List[RoleMapping], int]:
        smt: Select = select(AuthenticationRoleMapping)
        if method is not None: 
            smt = smt.where(AuthenticationRoleMapping.authentication == method)
        if identifiers is not None:
            smt = smt.where(AuthenticationRoleMapping.identifier.in_(identifiers))
        if roles is not None:
            smt = smt.where(AuthenticationRoleMapping.role.in_(roles))
        all_roles = db.session().execute(smt).all()
        return [self._map_to_role_mapping(i[0]) for i in set(all_roles)], len(all_roles)

    def create(self, method: AuthenticationMethod, identifier: str, roles: List[Roles]) -> None:
        session: Session = db.session
        smt: Insert = insert(AuthenticationRoleMapping).values(
            [
                {
                    'identifier': identifier,
                    'authentication': method,
                    'role': r
                } for r in roles
            ]
        )
        session.execute(smt)

        if method == AuthenticationMethod.USER:
            # in case a NainA is created put is_naina to true for compatibility
            if len(set([Roles.ADMIN_WRITE, Roles.ADMIN_READ, Roles.NETWORK_WRITE, Roles.NETWORK_READ])&set(roles)) == 4:
                adherent = session.query(Adherent).filter(Adherent.login == identifier).one_or_none()
                smt = update(Adherent).where(Adherent.id == adherent.id).values(is_naina=True)
                session.execute(smt)

    def delete(self, id: int) -> None:
        session: Session = db.session
        role_mapping = session.query(AuthenticationRoleMapping).where(AuthenticationRoleMapping.id == id).one()
        if role_mapping.authentication == AuthenticationMethod.USER:
            adherent = session.query(Adherent).filter(Adherent.login == role_mapping.identifier).one_or_none()
            smt = update(Adherent).where(Adherent.id == adherent.id).values(is_naina=False)
            session.execute(smt)
            

        smt = delete(AuthenticationRoleMapping).where(AuthenticationRoleMapping.id == id)
        session.execute(smt)

        # force reset nainA column in Adherent for compatibility

    def user_id_from_username(self, login: str) -> int:
        return db.session.execute(select(Adherent.id).where((Adherent.login == login) | (Adherent.ldap_login == login))).scalar()
    
    def _map_to_role_mapping(self, role: AuthenticationRoleMapping) -> RoleMapping:
        return RoleMapping(
            id=role.id,
            identifier=role.identifier,
            role=role.role.value,
            authentication=role.authentication.value
        )
