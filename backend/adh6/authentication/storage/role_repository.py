from typing import Any

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from adh6.entity import RoleMapping
from adh6.member.storage.models import Adherent

from ...exceptions import MemberNotFoundError
from ..enums import AuthenticationMethod, Roles
from ..interfaces import RoleRepository
from .models import AuthenticationRoleMapping


class RoleSQLRepository(RoleRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: int) -> Any:  # todo
        smt = select(AuthenticationRoleMapping).where(AuthenticationRoleMapping.id == id)
        result = await self.session.scalar(smt)
        return result

    async def find(
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

        all_roles = (await self.session.execute(smt)).all()
        return [self._map_to_role_mapping(i[0]) for i in set(all_roles)], len(all_roles)

    async def create(self, method: AuthenticationMethod, identifier: str, roles: list[Roles]) -> None:
        smt = insert(AuthenticationRoleMapping).values(
            [{"identifier": identifier, "authentication": method, "role": r} for r in roles]
        )
        await self.session.execute(smt)

        # in case a NainA is created put is_naina to true for compatibility
        if method == AuthenticationMethod.USER and (
            len(
                {
                    Roles.ADMIN_WRITE,
                    Roles.ADMIN_READ,
                    Roles.NETWORK_WRITE,
                    Roles.NETWORK_READ,
                }
                & set(roles)
            )
            == 4
        ):
            stmt = select(Adherent).where(Adherent.login == identifier)
            adherent = await self.session.scalar(stmt)
            if adherent:
                smt = update(Adherent).where(Adherent.id == adherent.id).values(is_naina=True)
                await self.session.execute(smt)

    async def delete(self, id: int) -> None:
        stmt = select(AuthenticationRoleMapping).where(AuthenticationRoleMapping.id == id)
        role_mapping = await self.session.scalar(stmt)

        if role_mapping and role_mapping.authentication == AuthenticationMethod.USER:
            stmt_adherent = select(Adherent).where(Adherent.login == role_mapping.identifier)
            adherent = await self.session.scalar(stmt_adherent)
            if adherent:
                smt = update(Adherent).where(Adherent.id == adherent.id).values(is_naina=False)
                await self.session.execute(smt)

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
            role=role.role.value,
            authentication=role.authentication.value,
        )
