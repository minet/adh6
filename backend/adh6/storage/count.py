from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession


async def count_rows(session: AsyncSession, stmt: Select[Any]) -> int:
    """Count the rows matched by stmt with a SQL COUNT, without fetching them."""
    subquery = stmt.order_by(None).limit(None).offset(None).subquery()
    return await session.scalar(select(func.count()).select_from(subquery)) or 0
