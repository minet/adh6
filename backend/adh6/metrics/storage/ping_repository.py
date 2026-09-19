from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from adh6.metrics.interfaces import PingRepository


class PingSQLRepository(PingRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def ping(self) -> bool:
        result = await self.session.execute(text("SELECT 1"))
        return result.scalar_one() == 1
