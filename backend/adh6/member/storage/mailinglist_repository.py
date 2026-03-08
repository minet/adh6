from collections.abc import Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..interfaces.mailinglist_repository import MailinglistRepository
from .models import Adherent


class MailinglistSQLReposiroty(MailinglistRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_from_member(self, member_id: int) -> int:
        smt = select(Adherent.mail_membership).where(Adherent.id == member_id)
        result = await self.session.execute(smt)
        return result.scalar_one()

    async def update_from_member(self, member_id: int, value: int) -> None:
        smt = update(Adherent).where(Adherent.id == member_id).values(mail_membership=value)
        await self.session.execute(smt)

    async def list_members(self, value: int) -> Sequence[int]:
        smt = select(Adherent.id).where(Adherent.mail_membership == value)
        result = await self.session.execute(smt)
        return result.scalars().all()
