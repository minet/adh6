from typing import List

from sqlalchemy import select, update
from sqlalchemy.orm import Session
from adh6.constants import CTX_SQL_SESSION
from adh6.member.interfaces.mailinglist_repository import MailinglistRepository
from adh6.storage.sql.models import Adherent

class MailinglistSQLReposiroty(MailinglistRepository):
    def get_from_member(self, ctx, member_id: int) -> int:
        session: Session = ctx.get(CTX_SQL_SESSION)
        smt = select(Adherent.mail_membership).where(Adherent.id == member_id)
        return session.execute(smt).scalar_one()

    def update_from_member(self, ctx, member_id: int, value: int) -> None:
        session: Session = ctx.get(CTX_SQL_SESSION)
        smt = update(Adherent).where(Adherent.id == member_id).values(mail_membership=value)
        session.execute(smt)

    def list_members(self, ctx, value: int) -> List[int]:
        session: Session = ctx.get(CTX_SQL_SESSION)
        smt = select(Adherent.id).where(Adherent.mail_membership == value)
        return session.execute(smt).scalars().all()
