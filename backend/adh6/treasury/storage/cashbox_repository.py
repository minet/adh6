"""
Implements everything related to actions on the SQL database.
"""

import decimal
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..interfaces import CashboxRepository
from .models import Caisse as SQLCashbox


class CashboxSQLRepository(CashboxRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def update(self, value_modifier=None, transaction=None):
        now = datetime.now()

        fond, coffre = map(decimal.Decimal, await self.get())

        fond += decimal.Decimal(value_modifier)

        cashbox_update = SQLCashbox(
            fond=fond,
            coffre=coffre,
            date=now,
            created_at=now,
            updated_at=now,
            linked_transaction=transaction.id if transaction is not None else None,
        )

        self.session.add(cashbox_update)

    async def get(self) -> tuple[float, float]:
        stmt = select(SQLCashbox).order_by(SQLCashbox.id.desc()).limit(1)
        result = await self.session.execute(stmt)
        r = result.scalars().all()[0]
        return r.fond, r.coffre  # type: ignore  # TODO: fix typing
