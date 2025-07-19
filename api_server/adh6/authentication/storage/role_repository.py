from typing import Any

from sqlalchemy import delete, insert, select, update
from sqlalchemy.sql import Select

from adh6.entity import RoleMapping
from adh6.member.storage.models import Adherent
from adh6.storage import db

from ..enums import AuthenticationMethod, Roles
from ..interfaces import RoleRepository
from .models import AuthenticationRoleMapping


class RoleSQLRepository(RoleRepository):
    def get(self, id: int) -> Any:  # todo
        smt = select(AuthenticationRoleMapping).where(AuthenticationRoleMapping.id == id)
        with db.sessionmaker() as session:
            result = session.execute(smt).scalar_one_or_none()
        return result

    def find(
        self,
        method: AuthenticationMethod | None = None,
        identifiers: list[str] | None = None,
        roles: list[Roles] | None = None,
    ) -> tuple[list[RoleMapping], int]:
        smt: Select = select(AuthenticationRoleMapping)
        if method is not None:
            smt = smt.where(AuthenticationRoleMapping.authentication == method)
        if identifiers is not None:
            smt = smt.where(AuthenticationRoleMapping.identifier.in_(identifiers))
        if roles is not None:
            smt = smt.where(AuthenticationRoleMapping.role.in_(roles))
        with db.sessionmaker() as session:
            all_roles = session.execute(smt).all()
        return [self._map_to_role_mapping(i[0]) for i in set(all_roles)], len(all_roles)

    def create(self, method: AuthenticationMethod, identifier: str, roles: list[Roles]) -> None:
        smt = insert(AuthenticationRoleMapping).values(
            [{"identifier": identifier, "authentication": method, "role": r} for r in roles]
        )
        with db.sessionmaker.begin() as session:
            session.execute(smt)

        # in case a NainA is created put is_naina to true for compatibility
        if method == AuthenticationMethod.USER and (
            len({Roles.ADMIN_WRITE, Roles.ADMIN_READ, Roles.NETWORK_WRITE, Roles.NETWORK_READ} & set(roles)) == 4
        ):
            with db.sessionmaker.begin() as session:
                adherent = session.query(Adherent).filter(Adherent.login == identifier).scalar()
                smt = update(Adherent).where(Adherent.id == adherent.id).values(is_naina=True)
                session.execute(smt)

    def delete(self, id: int) -> None:
        with db.sessionmaker.begin() as session:
            role_mapping = session.query(AuthenticationRoleMapping).where(AuthenticationRoleMapping.id == id).one()
            if role_mapping.authentication == AuthenticationMethod.USER:
                adherent = session.query(Adherent).filter(Adherent.login == role_mapping.identifier).scalar()
                smt = update(Adherent).where(Adherent.id == adherent.id).values(is_naina=False)
                session.execute(smt)

            smt = delete(AuthenticationRoleMapping).where(AuthenticationRoleMapping.id == id)
            session.execute(smt)

        # force reset nainA column in Adherent for compatibility

    def user_id_from_username(self, login: str) -> int:
        with db.sessionmaker() as session:
            result = session.execute(
                select(Adherent.id).where((Adherent.login == login) | (Adherent.ldap_login == login))
            ).scalar_one()
        return result

    def _map_to_role_mapping(self, role: AuthenticationRoleMapping) -> RoleMapping:
        return RoleMapping(
            id=role.id, identifier=role.identifier, role=role.role.value, authentication=role.authentication.value
        )
