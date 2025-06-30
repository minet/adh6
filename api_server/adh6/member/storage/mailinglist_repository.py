from collections.abc import Sequence

from sqlalchemy import select, update

from adh6.storage import db

from ..interfaces.mailinglist_repository import MailinglistRepository
from .models import Adherent


class MailinglistSQLReposiroty(MailinglistRepository):
    def get_from_member(self, member_id: int) -> int:
        smt = select(Adherent.mail_membership).where(Adherent.id == member_id)
        with db.sessionmaker() as session:
            return session.execute(smt).scalar_one()

    def update_from_member(self, member_id: int, value: int) -> None:
        smt = update(Adherent).where(Adherent.id == member_id).values(mail_membership=value)
        with db.sessionmaker() as session:
            session.execute(smt)

    def list_members(self, value: int) -> Sequence[int]:
        smt = select(Adherent.id).where(Adherent.mail_membership == value)
        with db.sessionmaker() as session:
            return session.execute(smt).scalars().all()
