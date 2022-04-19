# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from datetime import datetime

from sqlalchemy.orm.session import Session
from src.util.log import LOG
from src.util.context import log_extra
from typing import List, Optional, Tuple, Union

from sqlalchemy.orm import aliased

from src.constants import CTX_SQL_SESSION, DEFAULT_LIMIT, DEFAULT_OFFSET, CTX_ADMIN
from src.entity import AbstractTransaction, Transaction, Product
from src.exceptions import AccountNotFoundError, MemberNotFoundError, MemberTransactionAmountMustBeGreaterThan, PaymentMethodNotFoundError, ProductNotFoundError, TransactionNotFoundError, UnknownPaymentMethod
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.sql.account_repository import _map_account_sql_to_entity
from src.interface_adapter.sql.member_repository import _map_member_sql_to_entity
from src.interface_adapter.sql.model.models import Transaction as SQLTransaction, Product as SQLProduct, Account, PaymentMethod, Adherent
from src.interface_adapter.sql.payment_method_repository import _map_payment_method_sql_to_entity
from src.interface_adapter.sql.track_modifications import track_modifications
from src.use_case.interface.transaction_repository import TransactionRepository

auto_validate_payment_method = ["Liquide", "Carte bancaire"]

class TransactionSQLRepository(TransactionRepository):
    @log_call
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None,
                  filter_:  AbstractTransaction = None) -> Tuple[List[Transaction], int]:
        session: Session= ctx.get(CTX_SQL_SESSION)

        account_source = aliased(Account)
        account_destination = aliased(Account)

        query= session.query(SQLTransaction)
        query= query.join(account_source, account_source.id == SQLTransaction.dst)
        query= query.join(account_destination, account_destination.id == SQLTransaction.src)

        if filter_.id is not None:
            query= query.filter(SQLTransaction.id == filter_.id)
        if filter_.payment_method is not None:
            if isinstance(filter_.payment_method, PaymentMethod):
                filter_.payment_method = filter_.payment_method.id
            query= query.filter(SQLTransaction.type == filter_.payment_method)
        if terms:
            query= query.filter(
                (SQLTransaction.name.contains(terms))
            )
        if filter_.pending_validation is not None:
            query= query.filter(
                (SQLTransaction.pending_validation == filter_.pending_validation)
            )
        if filter_.src is not None and filter_.dst is not None and filter_.src == filter_.dst:
            query= query.filter(
                (SQLTransaction.src == filter_.src) |
                (SQLTransaction.dst == filter_.dst)
            )
        elif filter_.src is not None:
            query= query.filter(SQLTransaction.src == filter_.src)
        elif filter_.dst is not None:
            query= query.filter(SQLTransaction.dst == filter_.dst)

        count = query.count()
        query= query.order_by(SQLTransaction.timestamp.desc())
        query= query.offset(offset)
        query= query.limit(limit)
        r = query.all()

        return list(map(_map_transaction_sql_to_entity, r)), count

    @log_call
    def create(self, ctx, abstract_transaction: AbstractTransaction) -> object:
        session: Session= ctx.get(CTX_SQL_SESSION)

        now = datetime.now()

        admin_id = ctx.get(CTX_ADMIN).id
        author_ref = session.query(Adherent).filter(Adherent.id == admin_id).one_or_none()
        if not author_ref:
            raise MemberNotFoundError(abstract_transaction.author)

        account_src = None
        if abstract_transaction.src is not None:
            account_src = session.query(Account).filter(Account.id == abstract_transaction.src).one_or_none()
            if not account_src:
                raise AccountNotFoundError(abstract_transaction.src)

        account_dst = None
        if abstract_transaction.dst is not None:
            account_dst = session.query(Account).filter(Account.id == abstract_transaction.dst).one_or_none()
            if not account_dst:
                raise AccountNotFoundError(abstract_transaction.dst)

        method = None
        if abstract_transaction.payment_method is not None:
            method = session.query(PaymentMethod).filter(
                PaymentMethod.id == abstract_transaction.payment_method).one_or_none()
            if not method:
                raise PaymentMethodNotFoundError(abstract_transaction.payment_method)

        transaction = SQLTransaction(
            src_account=account_src,
            dst_account=account_dst,
            value=abstract_transaction.value,
            name=abstract_transaction.name,
            timestamp=now,
            attachments="",
            payment_method=method,
            author=author_ref,
            pending_validation=abstract_transaction.pending_validation if abstract_transaction.pending_validation else False
        )

        with track_modifications(ctx, session, transaction):
            session.add(transaction)
        session.flush()

        return _map_transaction_sql_to_entity(transaction)

    def update(self, ctx, abstract_transaction: AbstractTransaction, override=False) -> object:
        raise NotImplementedError

    @log_call
    def validate(self, ctx, id) -> None:
        session: Session = ctx.get(CTX_SQL_SESSION)

        query= session.query(SQLTransaction)
        query= query.filter(SQLTransaction.id == id)

        transaction = query.one_or_none()
        if transaction is None:
            raise TransactionNotFoundError(str(id))

        with track_modifications(ctx, session, transaction):
            transaction.pending_validation = False
        session.flush()

    @log_call
    def delete(self, ctx, object_id) -> None:
        session: Session = ctx.get(CTX_SQL_SESSION)

        transaction = session.query(SQLTransaction).filter(SQLTransaction.id == object_id).one_or_none()

        if transaction is None:
            raise TransactionNotFoundError(object_id)

        with track_modifications(ctx, session, transaction):
            session.delete(transaction)
        session.flush()

    def add_member_payment_record(self, ctx, amount_in_cents: int, title: str, member_username: str, payment_method_name: str, membership_uuid: str) -> None:
        if amount_in_cents < 900:
            raise MemberTransactionAmountMustBeGreaterThan(str(amount_in_cents))

        minet_frais_asso_name: str = "MiNET frais asso"
        minet_frais_techniques_name: str = "MiNET frais techniques"
        LOG.debug("sql_money_repository_add_payment_record",
                  extra=log_extra(ctx, amount=amount_in_cents / 100, title=title, username=member_username,
                                  payment_method=payment_method_name))
        now = datetime.now()
        session: Session = ctx.get(CTX_SQL_SESSION)

        adherent = session.query(Adherent).filter(Adherent.login == member_username).one_or_none()
        if adherent is None:
            raise MemberNotFoundError(member_username)
        
        account: Account = session.query(Account).filter(Account.adherent_id == adherent.id).one_or_none()
        if account is None:
            raise AccountNotFoundError(member_username)
        
        LOG.debug("sql_money_repository_get_minet_frais_asso_account", extra=log_extra(ctx, account_name=minet_frais_asso_name))
        minet_asso_account: Account = session.query(Account).filter(Account.name == minet_frais_asso_name).filter(Account.pinned == True).one_or_none()
        if minet_asso_account is None:
            raise AccountNotFoundError(minet_frais_asso_name)
        minet_technique_account: Account = session.query(Account).filter(Account.name == minet_frais_techniques_name).filter(Account.pinned == True).one_or_none()
        if minet_technique_account is None:
            raise AccountNotFoundError(minet_frais_techniques_name)

        payment_method: PaymentMethod = session.query(PaymentMethod).filter(PaymentMethod.name == payment_method_name).one_or_none()
        if payment_method is None:
            raise UnknownPaymentMethod(payment_method_name)

        frais_asso_transaction: SQLTransaction = SQLTransaction(
            value=9.00,
            timestamp=now,
            src_account=account,
            dst_account=minet_asso_account,
            author=adherent,
            pending_validation=payment_method.name not in auto_validate_payment_method,
            name=title,
            attachments="",
            payment_method=payment_method,
            membership_uuid=membership_uuid,
            is_archive=False
        )
        session.add(frais_asso_transaction)

        amount_in_cents = amount_in_cents - 900
        if amount_in_cents > 0:
            frais_asso_transaction: SQLTransaction = SQLTransaction(
                value=amount_in_cents/100,
                timestamp=now,
                src_account=account,
                dst_account=minet_technique_account,
                author=adherent,
                pending_validation=payment_method.name not in auto_validate_payment_method,
                name=title,
                attachments="",
                payment_method=payment_method,
                membership_uuid=membership_uuid,
                is_archive=False
            )
            session.add(frais_asso_transaction)

        session.flush()
    
    def add_products_payment_record(self, ctx, member_id: int, products: List[Union[Product, int]], payment_method_name: str, membership_uuid: Optional[str]) -> None:
        now = datetime.now()
        session: Session = ctx.get(CTX_SQL_SESSION)
        LOG.debug("sql_money_repository_add_products_transaction_record", extra=log_extra(ctx, number_products=len(products)))

        adherent: Adherent = session.query(Adherent).filter(Adherent.id == member_id).one_or_none()
        if adherent is None:
            raise MemberNotFoundError(str(member_id))
        member_account: Account = session.query(Account).filter(Account.adherent_id == member_id).one_or_none()
        if member_account is None:
            raise AccountNotFoundError(str(adherent.login))
        minet_technique_account: Account = session.query(Account).filter(Account.name == "MiNET frais techniques").filter(Account.pinned == True).one_or_none()
        if minet_technique_account is None:
            raise AccountNotFoundError("MiNET frais techniques")
        payment_method: PaymentMethod = session.query(PaymentMethod).filter(PaymentMethod.name == payment_method_name).one_or_none()
        if payment_method is None:
            raise UnknownPaymentMethod(payment_method_name)
        for p in products:
            if isinstance(p, Product):
                p = p.id
            
            product: SQLProduct = session.query(SQLProduct).filter(SQLProduct.id == p).one_or_none()
            if product is None:
                ProductNotFoundError(str(p))
            
            p_transaction: SQLTransaction = SQLTransaction(
                value=product.selling_price,
                timestamp=now,
                src_account=member_account,
                dst_account=minet_technique_account,
                author=adherent,
                pending_validation=payment_method.name not in auto_validate_payment_method,
                name=product.name,
                attachments="",
                payment_method=payment_method,
                membership_uuid=membership_uuid,
                is_archive=False
            )

            session.add(p_transaction)
        session.flush()


def _map_transaction_sql_to_entity(t: SQLTransaction) -> Transaction:
    """
    Map a Transaction object from SQLAlchemy to a Transaction (from the entity folder/layer).
    """
    return Transaction(
        id=t.id,
        src=_map_account_sql_to_entity(t.src_account),
        dst=_map_account_sql_to_entity(t.dst_account),
        timestamp=str(t.timestamp),
        name=t.name,
        value=t.value,
        payment_method=_map_payment_method_sql_to_entity(t.payment_method),
        attachments=[],
        author=_map_member_sql_to_entity(t.author),
        pending_validation=t.pending_validation
    )
