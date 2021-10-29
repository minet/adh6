# coding=utf-8
from datetime import datetime
from typing import List
from src.entity.product import Product
from sqlalchemy.orm.session import Session

from src.constants import CTX_SQL_SESSION, CTX_ADMIN
from src.exceptions import AccountNotFoundError, InvalidAdmin, MemberNotFoundError, UnknownPaymentMethod, MemberTransactionAmountMustBeGreaterThan
from src.interface_adapter.sql.model.models import Admin, Adherent, PaymentMethod, Transaction, Account
from src.use_case.interface.money_repository import MoneyRepository
from src.util.context import log_extra
from src.util.log import LOG


class MoneySQLRepository(MoneyRepository):
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
        session: Session = ctx.get(CTX_SQL_SESSION)
        admin = ctx.get(CTX_ADMIN)

        admin_sql = session.query(Adherent).join(Admin).filter(Adherent.id == admin.id).filter(Adherent.admin_id is not None).one_or_none()
        if admin_sql is None:
            raise InvalidAdmin()

        adherent = session.query(Adherent).filter(Adherent.login == member_username).one_or_none()
        if adherent is None:
            raise MemberNotFoundError(member_username)
        
        account: Account = session.query(Account).filter(Account.adherent_id == adherent.id).one_or_none()
        if account is None:
            raise AccountNotFoundError(member_username)
        
        LOG.debug("sql_money_repository_get_minet_frais_asso_account", extra=log_extra(ctx, account_name=minet_frais_asso_name))
        minet_asso_account: Account = session.query(Account).filter(Account.name == minet_frais_asso_name).one_or_none()
        if minet_asso_account is None:
            raise AccountNotFoundError(minet_frais_asso_name)
        minet_technique_account: Account = session.query(Account).filter(Account.name == minet_frais_techniques_name).one_or_none()
        if minet_technique_account is None:
            raise AccountNotFoundError(minet_frais_techniques_name)

        payment_method: PaymentMethod = session.query(PaymentMethod).filter(PaymentMethod.name == payment_method_name).one_or_none()
        if payment_method is None:
            raise UnknownPaymentMethod(payment_method_name)

        frai_asso_transaction: Transaction = Transaction(
            value=9.00,
            timestamp=now,
            src_account=account,
            dst_account=minet_asso_account,
            author=adherent,
            pending_validation=True,
            name=title,
            attachments=""
        )
        session.add(frai_asso_transaction)

        amount_in_cents = amount_in_cents - 900
        if amount_in_cents > 0:
            frai_asso_transaction: Transaction = Transaction(
                value=amount_in_cents/100,
                timestamp=now,
                src_account=account,
                dst_account=minet_technique_account,
                author=adherent,
                pending_validation=True,
                name=title,
                attachments=""
            )

        session.flush()
    
    def add_products_payment_record(self, ctx, products: List[Product]) -> None:
        session: Session = ctx.get(CTX_SQL_SESSION)
        LOG.debug("sql_money_repository_add_products_transaction_record", extra=log_extra(ctx, number_products=len(products)))
        pass

