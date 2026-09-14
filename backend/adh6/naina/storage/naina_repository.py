from datetime import UTC, datetime

from sqlalchemy import and_, delete, insert, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.authentication.enums import AuthenticationMethod, Roles
from adh6.authentication.storage.models import AuthenticationRoleMapping
from adh6.entity import Naina
from adh6.naina.interfaces import NainaRepository

_TEMPORARY_USER_ROLE = and_(
    AuthenticationRoleMapping.authentication == AuthenticationMethod.USER,
    AuthenticationRoleMapping.expires_at.is_not(None),
)


class NainaSQLRepository(NainaRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, identifier: str, roles: tuple[Roles, ...], expires_at: datetime) -> None:
        # Active grants all share the next cutoff, so anything earlier has already expired.
        await self.session.execute(
            delete(AuthenticationRoleMapping).where(
                _TEMPORARY_USER_ROLE,
                or_(
                    AuthenticationRoleMapping.identifier == identifier,
                    AuthenticationRoleMapping.expires_at < expires_at,
                ),
            )
        )
        await self.session.execute(
            insert(AuthenticationRoleMapping).values(
                [
                    {
                        "authentication": AuthenticationMethod.USER,
                        "identifier": identifier,
                        "role": role,
                        "expires_at": expires_at,
                    }
                    for role in roles
                ]
            )
        )

    async def find_active(self, now: datetime) -> list[Naina]:
        statement = (
            select(AuthenticationRoleMapping.identifier, AuthenticationRoleMapping.expires_at)
            .where(
                AuthenticationRoleMapping.authentication == AuthenticationMethod.USER,
                AuthenticationRoleMapping.expires_at > now,
            )
            .distinct()
            .order_by(AuthenticationRoleMapping.identifier)
        )
        rows = (await self.session.execute(statement)).all()
        return [Naina(login=login, expires_at=expires_at.replace(tzinfo=UTC)) for login, expires_at in rows]

    async def revoke(self, identifier: str) -> None:
        await self.session.execute(
            delete(AuthenticationRoleMapping).where(
                _TEMPORARY_USER_ROLE,
                AuthenticationRoleMapping.identifier == identifier,
            )
        )
