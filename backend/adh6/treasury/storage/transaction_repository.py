"""
Implements everything related to actions on the SQL database.
"""

from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity import AbstractTransaction, Transaction
from adh6.exceptions import PaymentMethodNotFoundError

from ..interfaces import TransactionRepository
from .models import PaymentMethod, Transaction as SQLTransaction


class TransactionSQLRepository(TransactionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, object_id: int) -> Transaction | None:
        stmt = select(SQLTransaction).where(SQLTransaction.id == object_id)
        obj = await self.session.scalar(stmt)
        return _map_transaction_sql_to_entity(obj) if obj else obj

    async def search_by(
        self,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        terms: str | None = None,
        filter_: AbstractTransaction | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> tuple[list[Transaction], int]:
        stmt = select(SQLTransaction)

        if filter_:
            if filter_.id is not None:
                stmt = stmt.where(SQLTransaction.id == filter_.id)
            if filter_.payment_method is not None:
                stmt = stmt.where(SQLTransaction.type == filter_.payment_method)
            if filter_.membership_uuid is not None:
                stmt = stmt.where(SQLTransaction.membership_uuid == filter_.membership_uuid)
            if filter_.product_type is not None:
                stmt = stmt.where(SQLTransaction.product_type == filter_.product_type)
            if filter_.product_id is not None:
                stmt = stmt.where(SQLTransaction.product_id == filter_.product_id)

        if from_date is not None:
            stmt = stmt.where(SQLTransaction.timestamp >= datetime.combine(from_date, datetime.min.time()))
        if to_date is not None:
            stmt = stmt.where(SQLTransaction.timestamp <= datetime.combine(to_date, datetime.max.time()))

        if terms:
            stmt = stmt.where(SQLTransaction.name.like(f"%{terms}%"))

        stmt = stmt.order_by(SQLTransaction.timestamp.desc())

        # Count
        count_result = await self.session.execute(stmt)
        count = len(count_result.all())

        # Apply pagination
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        r = result.scalars().all()

        return [_map_transaction_sql_to_entity(i) for i in r], count

    async def create(self, abstract_transaction: AbstractTransaction) -> object:
        now = datetime.now()

        method_id = None
        if abstract_transaction.payment_method is not None:
            method_stmt = select(PaymentMethod).where(PaymentMethod.id == abstract_transaction.payment_method)
            method = await self.session.scalar(method_stmt)
            if not method:
                raise PaymentMethodNotFoundError(abstract_transaction.payment_method)
            method_id = method.id

        transaction = SQLTransaction(
            value=abstract_transaction.value,
            name=abstract_transaction.name,
            timestamp=now,
            type=method_id,
            author_id=abstract_transaction.author,
            membership_uuid=abstract_transaction.membership_uuid,
            api_key_id=abstract_transaction.api_key_id,
            product_id=abstract_transaction.product_id,
            product_type=abstract_transaction.product_type,
        )

        self.session.add(transaction)
        await self.session.flush()

        return _map_transaction_sql_to_entity(transaction)

    def update(self, abstract_transaction: AbstractTransaction, override=False) -> object:
        raise NotImplementedError

    async def delete(self, object_id) -> None:
        stmt = select(SQLTransaction).where(SQLTransaction.id == object_id)
        transaction = await self.session.scalar(stmt)

        await self.session.delete(transaction)

    async def search_for_export(
        self,
        from_date: date,
        to_date: date,
    ) -> list[Transaction]:
        stmt = (
            select(SQLTransaction)
            .where(SQLTransaction.timestamp >= datetime.combine(from_date, datetime.min.time()))
            .where(SQLTransaction.timestamp <= datetime.combine(to_date, datetime.max.time()))
            .order_by(SQLTransaction.timestamp.asc())
        )
        result = await self.session.execute(stmt)
        return [_map_transaction_sql_to_entity(i) for i in result.scalars().all()]


def _map_transaction_sql_to_entity(t: SQLTransaction) -> Transaction:
    return Transaction(
        id=t.id,
        timestamp=t.timestamp,
        name=t.name,
        value=t.value,
        paymentMethod=t.type,
        author=t.author_id,
        membershipUuid=t.membership_uuid,
        apiKeyId=t.api_key_id,
        productId=t.product_id,
        productType=t.product_type,
    )
