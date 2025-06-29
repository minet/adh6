from datetime import datetime

from sqlalchemy import select, update

from adh6.storage import db

from ..interfaces.charter_repository import CharterRepository
from .models import Adherent


class CharterSQLRepository(CharterRepository):
    def get(self, charter_id: int, member_id: int) -> datetime | None:
        smt = select(Adherent.datesignedminet) if charter_id == 1 else select(Adherent.datesignedhosting)
        smt = smt.where(Adherent.id == member_id)
        return db.session.execute(smt).scalar_one()

    def get_members(self, charter_id: int) -> tuple[list[int], int]:
        smt = select(Adherent.id)
        smt = smt.where(
            Adherent.datesignedminet.isnot(None) if charter_id == 1 else Adherent.datesignedhosting.isnot(None)
        )
        r = db.session.execute(smt).scalars().all()
        return r, len(r)  # type: ignore  # TODO: fix typing

    def update(self, charter_id: int, member_id: int) -> None:
        smt = update(Adherent).where(Adherent.id == member_id)
        if charter_id == 1:
            smt = smt.values(datesignedminet=datetime.now())
        else:
            smt = smt.values(datesignedhosting=datetime.now())
        db.session.execute(smt)
