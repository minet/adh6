from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from ..interfaces import PingRepository


class PingSQLRepository(PingRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def ping(self) -> bool:
        try:
            result = await self.session.execute(text("SELECT 42 AS result"))
            rows = result.fetchall()
            if len(rows) != 1:
                return False

        except SQLAlchemyError:
            return False
        else:
            return rows == [(42,)]
