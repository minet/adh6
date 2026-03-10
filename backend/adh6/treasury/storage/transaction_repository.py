"""
Implements everything related to actions on the SQL database.
"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity import AbstractTransaction, Transaction
from adh6.exceptions import AccountNotFoundError, PaymentMethodNotFoundError

from ..interfaces import TransactionRepository
from .models import Account, PaymentMethod, Transaction as SQLTransaction

auto_validate_payment_method = ["Liquide", "Carte bancaire"]


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
    ) -> tuple[list[Transaction], int]:
        stmt = select(SQLTransaction)

        if filter_:
            if filter_.id is not None:
                stmt = stmt.where(SQLTransaction.id == filter_.id)
            if filter_.payment_method is not None:
                stmt = stmt.where(SQLTransaction.type == filter_.payment_method)
            if filter_.pending_validation is not None:
                stmt = stmt.where(SQLTransaction.pending_validation == filter_.pending_validation)
            if filter_.src is not None and filter_.dst is not None and filter_.src == filter_.dst:
                stmt = stmt.where((SQLTransaction.src == filter_.src) | (SQLTransaction.dst == filter_.dst))
            elif filter_.src is not None:
                stmt = stmt.where(SQLTransaction.src == filter_.src)
            elif filter_.dst is not None:
                stmt = stmt.where(SQLTransaction.dst == filter_.dst)

        if terms:
            stmt = stmt.where(SQLTransaction.name.like(f"%{terms}%"))

        # Count
        count_result = await self.session.execute(stmt)
        count = len(count_result.all())

        # Apply ordering and pagination
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        r = result.scalars().all()

        return [_map_transaction_sql_to_entity(i) for i in r], count

    async def create(self, abstract_transaction: AbstractTransaction) -> object:
        now = datetime.now()

        account_src_id = None
        if abstract_transaction.src is not None:
            account_src_stmt = select(Account).where(Account.id == abstract_transaction.src)
            account_src = await self.session.scalar(account_src_stmt)
            if not account_src:
                raise AccountNotFoundError(abstract_transaction.src)
            account_src_id = account_src.id

        account_dst_id = None
        if abstract_transaction.dst is not None:
            account_dst_stmt = select(Account).where(Account.id == abstract_transaction.dst)
            account_dst = await self.session.scalar(account_dst_stmt)
            if not account_dst:
                raise AccountNotFoundError(abstract_transaction.dst)
            account_dst_id = account_dst.id

        method_id = None
        if abstract_transaction.payment_method is not None:
            method_stmt = select(PaymentMethod).where(PaymentMethod.id == abstract_transaction.payment_method)
            method = await self.session.scalar(method_stmt)
            if not method:
                raise PaymentMethodNotFoundError(abstract_transaction.payment_method)
            method_id = method.id

        transaction = SQLTransaction(
            src=account_src_id,
            dst=account_dst_id,
            value=abstract_transaction.value,
            name=abstract_transaction.name,
            timestamp=now,
            attachments="",
            type=method_id,
            author_id=abstract_transaction.author,
            pending_validation=(
                abstract_transaction.pending_validation if abstract_transaction.pending_validation else False
            ),
        )

        self.session.add(transaction)
        await self.session.flush()
        mapped_transaction = _map_transaction_sql_to_entity(transaction)

        return mapped_transaction

    def update(self, abstract_transaction: AbstractTransaction, override=False) -> object:
        raise NotImplementedError

    async def validate(self, id) -> None:
        stmt = select(SQLTransaction).where(SQLTransaction.id == id)
        transaction = await self.session.scalar(stmt)

        transaction.pending_validation = False

    async def delete(self, object_id) -> None:
        stmt = select(SQLTransaction).where(SQLTransaction.id == object_id)
        transaction = await self.session.scalar(stmt)

        await self.session.delete(transaction)


def _map_transaction_sql_to_entity(t: SQLTransaction) -> Transaction:
    """
    Map a Transaction object from SQLAlchemy to a Transaction (from the entity folder/layer).
    """
    return Transaction(
        id=t.id,
        src=t.src,
        dst=t.dst,
        timestamp=str(t.timestamp),
        name=t.name,
        value=t.value,
        paymentMethod=t.type,
        attachments=[],
        author=t.author_id,
        pending_validation=t.pending_validation,
    )
