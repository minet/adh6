from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..interfaces.charter_repository import CharterRepository
from .models import Adherent


class CharterSQLRepository(CharterRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, charter_id: int, member_id: int) -> datetime | None:
        smt = select(Adherent.datesignedminet) if charter_id == 1 else select(Adherent.datesignedhosting)
        smt = smt.where(Adherent.id == member_id)

        result = await self.session.execute(smt)
        return result.scalar_one()

    async def get_members(self, charter_id: int) -> tuple[list[int], int]:
        smt = select(Adherent.id)
        smt = smt.where(
            Adherent.datesignedminet.isnot(None) if charter_id == 1 else Adherent.datesignedhosting.isnot(None)
        )
        result = await self.session.execute(smt)
        r = result.scalars().all()
        return r, len(r)  # type: ignore  # TODO: fix typing

    async def update(self, charter_id: int, member_id: int) -> None:
        smt = update(Adherent).where(Adherent.id == member_id)
        if charter_id == 1:
            smt = smt.values(datesignedminet=datetime.now())
        else:
            smt = smt.values(datesignedhosting=datetime.now())
        await self.session.execute(smt)
