from typing import List

from sqlalchemy import select, update
from adh6.storage import session

from .models import Adherent
from ..interfaces.mailinglist_repository import MailinglistRepository


class MailinglistSQLReposiroty(MailinglistRepository):
    def get_from_member(self, member_id: int) -> int:
        smt = select(Adherent.mail_membership).where(Adherent.id == member_id)
        return session.execute(smt).scalar_one()

    def update_from_member(self, member_id: int, value: int) -> None:
        smt = update(Adherent).where(Adherent.id == member_id).values(mail_membership=value)
        session.execute(smt)

    def list_members(self, value: int) -> List[int]:
        smt = select(Adherent.id).where(Adherent.mail_membership == value)
        return session.execute(smt).scalars().all()
