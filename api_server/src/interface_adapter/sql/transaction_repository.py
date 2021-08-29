# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from datetime import datetime

from sqlalchemy.orm.session import Session
from src.util.log import LOG
from src.util.context import log_extra
from typing import List, Tuple, Union

from sqlalchemy.orm import aliased

from src.constants import CTX_SQL_SESSION, DEFAULT_LIMIT, DEFAULT_OFFSET, CTX_ADMIN
from src.entity import AbstractTransaction, Transaction, Product
from src.exceptions import AccountNotFoundError, InvalidAdmin, MemberNotFoundError, MemberTransactionAmountMustBeGreaterThan, PaymentMethodNotFoundError, AdminNotFoundError, ProductNotFoundError, \
    TransactionNotFoundError, UnknownPaymentMethod
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.sql.account_repository import _map_account_sql_to_entity
from src.interface_adapter.sql.member_repository import _map_member_sql_to_entity
from src.interface_adapter.sql.model.models import Admin, Transaction as SQLTransaction, Product as SQLProduct, Account, PaymentMethod, Adherent
from src.interface_adapter.sql.payment_method_repository import _map_payment_method_sql_to_entity
from src.interface_adapter.sql.track_modifications import track_modifications
from src.use_case.interface.transaction_repository import TransactionRepository


class TransactionSQLRepository(TransactionRepository):
    @log_call
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None,
                  filter_: AbstractTransaction = None) -> Tuple[List[Transaction], int]:
        s = ctx.get(CTX_SQL_SESSION)

        account_source = aliased(Account)
        account_destination = aliased(Account)

        q = s.query(SQLTransaction)
        q = q.join(account_source, account_source.id == SQLTransaction.dst)
        q = q.join(account_destination, account_destination.id == SQLTransaction.src)

        if filter_.id is not None:
            q = q.filter(SQLTransaction.id == filter_.id)
        if filter_.payment_method is not None:
            if isinstance(filter_.payment_method, PaymentMethod):
                filter_.payment_method = filter_.payment_method.id
            q = q.filter(SQLTransaction.type == filter_.payment_method)
        if terms:
            q = q.filter(
                (SQLTransaction.name.contains(terms))
            )
        if filter_.pending_validation is not None:
            q = q.filter(
                (SQLTransaction.pending_validation == filter_.pending_validation)
            )
        if filter_.src is not None and filter_.dst is not None and filter_.src == filter_.dst:
            q = q.filter(
                (SQLTransaction.src == filter_.src) |
                (SQLTransaction.dst == filter_.dst)
            )
        elif filter_.src is not None:
            q = q.filter(SQLTransaction.src == filter_.src)
        elif filter_.dst is not None:
            q = q.filter(SQLTransaction.dst == filter_.dst)

        count = q.count()
        q = q.order_by(SQLTransaction.timestamp.desc())
        q = q.offset(offset)
        q = q.limit(limit)
        r = q.all()

        return list(map(_map_transaction_sql_to_entity, r)), count

    @log_call
    def create(self, ctx, abstract_transaction: AbstractTransaction) -> object:
        s = ctx.get(CTX_SQL_SESSION)

        now = datetime.now()

        admin_id = ctx.get(CTX_ADMIN).id
        author_ref = s.query(Adherent).join(Admin) \
            .filter(Adherent.id == admin_id) \
            .filter(Adherent.admin is not None).one_or_none()
        if not author_ref:
            raise AdminNotFoundError(abstract_transaction.author)

        account_src = None
        if abstract_transaction.src is not None:
            account_src = s.query(Account).filter(Account.id == abstract_transaction.src).one_or_none()
            if not account_src:
                raise AccountNotFoundError(abstract_transaction.src)

        account_dst = None
        if abstract_transaction.dst is not None:
            account_dst = s.query(Account).filter(Account.id == abstract_transaction.dst).one_or_none()
            if not account_dst:
                raise AccountNotFoundError(abstract_transaction.dst)

        method = None
        if abstract_transaction.payment_method is not None:
            method = s.query(PaymentMethod).filter(
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
            pending_validation=abstract_transaction.pending_validation
        )

        with track_modifications(ctx, s, transaction):
            s.add(transaction)
        s.flush()

        return _map_transaction_sql_to_entity(transaction)

    def update(self, ctx, abstract_transaction: AbstractTransaction, override=False) -> object:
        raise NotImplementedError

    @log_call
    def validate(self, ctx, transaction_id) -> None:
        s: Session = ctx.get(CTX_SQL_SESSION)

        q = s.query(SQLTransaction)
        q = q.filter(SQLTransaction.id == transaction_id)

        transaction = q.one_or_none()
        if transaction is None:
            raise TransactionNotFoundError(str(transaction_id))

        with track_modifications(ctx, s, transaction):
            transaction.pending_validation = False
        s.flush()

    @log_call
    def delete(self, ctx, object_id) -> None:
        s: Session = ctx.get(CTX_SQL_SESSION)

        transaction = s.query(SQLTransaction).filter(SQLTransaction.id == object_id).one_or_none()

        if transaction is None:
            raise TransactionNotFoundError(object_id)

        with track_modifications(ctx, s, transaction):
            s.delete(transaction)
        s.flush()

    def add_member_payment_record(self, ctx, amount_in_cents: int, title: str, member_username: str,
                                  payment_method_name: str) -> None:
        if amount_in_cents < 900:
            raise MemberTransactionAmountMustBeGreaterThan(str(amount_in_cents))

        minet_frais_asso_name: str = "MiNET frais asso"
        minet_frais_techniques_name: str = "MiNET frais techniques"
        LOG.debug("sql_money_repository_add_payment_record",
                  extra=log_extra(ctx, amount=amount_in_cents / 100, title=title, username=member_username,
                                  payment_method=payment_method_name))
        now = datetime.now()
        s: Session = ctx.get(CTX_SQL_SESSION)
        admin = ctx.get(CTX_ADMIN)

        admin_sql = s.query(Adherent).join(Admin).filter(Adherent.id == admin.id).filter(Adherent.admin_id is not None).one_or_none()
        if admin_sql is None:
            raise InvalidAdmin()

        adherent = s.query(Adherent).filter(Adherent.login == member_username).one_or_none()
        if adherent is None:
            raise MemberNotFoundError(member_username)
        
        account: Account = s.query(Account).filter(Account.adherent_id == adherent.id).one_or_none()
        if account is None:
            raise AccountNotFoundError(member_username)
        
        LOG.debug("sql_money_repository_get_minet_frais_asso_account", extra=log_extra(ctx, account_name=minet_frais_asso_name))
        minet_asso_account: Account = s.query(Account).filter(Account.name == minet_frais_asso_name).one_or_none()
        if minet_asso_account is None:
            raise AccountNotFoundError(minet_frais_asso_name)
        minet_technique_account: Account = s.query(Account).filter(Account.name == minet_frais_techniques_name).one_or_none()
        if minet_technique_account is None:
            raise AccountNotFoundError(minet_frais_techniques_name)

        payment_method: PaymentMethod = s.query(PaymentMethod).filter(PaymentMethod.name == payment_method_name).one_or_none()
        if payment_method is None:
            raise UnknownPaymentMethod(payment_method_name)

        frai_asso_transaction: SQLTransaction = SQLTransaction(
            value=9.00,
            timestamp=now,
            src_account=account,
            dst_account=minet_asso_account,
            author=adherent,
            pending_validation=True,
            name=title,
            attachments="",
            payment_method=payment_method
        )
        s.add(frai_asso_transaction)

        amount_in_cents = amount_in_cents - 900
        if amount_in_cents > 0:
            frai_asso_transaction: SQLTransaction = SQLTransaction(
                value=amount_in_cents/100,
                timestamp=now,
                src_account=account,
                dst_account=minet_technique_account,
                author=adherent,
                pending_validation=True,
                name=title,
                attachments="",
                payment_method=payment_method
            )

        s.flush()
    
    def add_products_payment_record(self, ctx, member_id: int, products: List[Union[Product, int]], payment_method_name: str) -> None:
        now = datetime.now()
        s: Session = ctx.get(CTX_SQL_SESSION)
        LOG.debug("sql_money_repository_add_products_transaction_record", extra=log_extra(ctx, number_products=len(products)))

        adherent: Adherent = s.query(Adherent).filter(Adherent.id == member_id).one_or_none()
        if adherent is None:
            raise MemberNotFoundError(str(member_id))
        member_account: Account = s.query(Account).filter(Account.adherent_id == member_id).one_or_none()
        if member_account is None:
            raise AccountNotFoundError(str(adherent.login))
        minet_technique_account: Account = s.query(Account).filter(Account.name == "MiNET frais techniques").one_or_none()
        if minet_technique_account is None:
            raise AccountNotFoundError("MiNET frais techniques")
        payment_method: PaymentMethod = s.query(PaymentMethod).filter(PaymentMethod.name == payment_method_name).one_or_none()
        if payment_method is None:
            raise UnknownPaymentMethod(payment_method_name)
        for p in products:
            if isinstance(p, Product):
                p = p.id
            
            product: SQLProduct = s.query(SQLProduct).filter(SQLProduct.id == p).one_or_none()
            if product is None:
                ProductNotFoundError(str(p))
            
            p_transaction: SQLTransaction = SQLTransaction(
                value=product.selling_price,
                timestamp=now,
                src_account=member_account,
                dst_account=minet_technique_account,
                author=adherent,
                pending_validation=True,
                name=product.name,
                attachments="",
                payment_method=payment_method
            )

            s.add(p_transaction)
        s.flush()


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
