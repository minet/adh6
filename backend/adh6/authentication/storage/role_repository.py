from datetime import UTC, datetime
from typing import Any

from sqlalchemy import and_, delete, insert, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import ColumnElement, Select

from adh6.authentication.enums import AuthenticationMethod, Roles
from adh6.authentication.interfaces import RoleRepository
from adh6.entity import Role, RoleMapping
from adh6.exceptions import MemberNotFoundError
from adh6.member.storage.models import Adherent

from .models import AuthenticationRoleMapping


class RoleSQLRepository(RoleRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: int) -> Any:
        smt = select(AuthenticationRoleMapping).where(
            AuthenticationRoleMapping.id == id,
            AuthenticationRoleMapping.expires_at.is_(None),
        )
        return await self.session.scalar(smt)

    async def find(
        self,
        method: AuthenticationMethod | None = None,
        identifiers: list[str] | None = None,
        roles: list[Roles] | None = None,
    ) -> tuple[list[RoleMapping], int]:
        smt: Select[tuple[AuthenticationRoleMapping]] = select(AuthenticationRoleMapping).where(
            AuthenticationRoleMapping.expires_at.is_(None)
        )
        if method is not None:
            smt = smt.where(AuthenticationRoleMapping.authentication == method)
        if identifiers is not None:
            smt = smt.where(AuthenticationRoleMapping.identifier.in_(identifiers))
        if roles is not None:
            smt = smt.where(AuthenticationRoleMapping.role.in_(roles))

        rows = (await self.session.execute(smt)).all()
        unique_roles = {row[0].id: row[0] for row in rows}
        return [self._map_to_role_mapping(role) for role in unique_roles.values()], len(rows)

    async def find_for_oidc_identity(self, groups: list[str], username: str | None) -> list[RoleMapping]:
        conditions: list[ColumnElement[bool]] = []
        if groups:
            conditions.append(
                and_(
                    AuthenticationRoleMapping.authentication == AuthenticationMethod.OIDC,
                    AuthenticationRoleMapping.identifier.in_(groups),
                )
            )
        if username:
            conditions.append(
                and_(
                    AuthenticationRoleMapping.authentication == AuthenticationMethod.USER,
                    AuthenticationRoleMapping.identifier == username,
                )
            )
        if not conditions:
            return []

        rows = (
            await self.session.execute(
                select(AuthenticationRoleMapping).where(
                    or_(*conditions),
                    or_(
                        AuthenticationRoleMapping.expires_at.is_(None),
                        AuthenticationRoleMapping.expires_at > _naive_utc_now(),
                    ),
                )
            )
        ).all()
        unique_mappings = {mapping.id: mapping for (mapping,) in rows}
        return [self._map_to_role_mapping(mapping) for mapping in unique_mappings.values()]

    async def create(self, method: AuthenticationMethod, identifier: str, roles: list[Roles]) -> None:
        smt = insert(AuthenticationRoleMapping).values(
            [{"identifier": identifier, "authentication": method, "role": r} for r in roles]
        )
        await self.session.execute(smt)

    async def delete(self, id: int) -> None:
        smt = delete(AuthenticationRoleMapping).where(AuthenticationRoleMapping.id == id)
        await self.session.execute(smt)

    async def user_id_from_username(self, login: str) -> int:
        result = await self.session.execute(
            select(Adherent.id).where((Adherent.login == login) | (Adherent.ldap_login == login))
        )
        user_id = result.scalar_one_or_none()
        if user_id is None:
            raise MemberNotFoundError(login)
        return user_id

    def _map_to_role_mapping(self, role: AuthenticationRoleMapping) -> RoleMapping:
        return RoleMapping(
            id=role.id,
            identifier=role.identifier,
            role=Role(role.role.value),
            authentication=role.authentication.value,
        )


def _naive_utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)
