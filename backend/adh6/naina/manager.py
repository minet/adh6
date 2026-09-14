from datetime import UTC, datetime

from adh6.authentication.enums import Roles
from adh6.entity import Naina
from adh6.exceptions import MemberNotFoundError
from adh6.member.interfaces import MemberRepository

from .expiration import next_naina_expiration
from .interfaces import NainaRepository

NAINA_ROLES = (
    Roles.ADMIN_READ,
    Roles.ADMIN_WRITE,
    Roles.NETWORK_READ,
    Roles.NETWORK_WRITE,
)


class NainaManager:
    def __init__(self, repository: NainaRepository, member_repository: MemberRepository) -> None:
        self.repository = repository
        self.member_repository = member_repository

    async def create(self, identifier: str) -> None:
        if not await self.member_repository.get_by_login(identifier):
            raise MemberNotFoundError(identifier)

        await self.repository.create(
            identifier=identifier,
            roles=NAINA_ROLES,
            expires_at=next_naina_expiration(_utc_now()),
        )

    async def search(self) -> list[Naina]:
        return await self.repository.find_active(_utc_now().replace(tzinfo=None))

    async def revoke(self, identifier: str) -> None:
        await self.repository.revoke(identifier)


def _utc_now() -> datetime:
    return datetime.now(UTC)
