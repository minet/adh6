from datetime import datetime
from typing import List, Tuple

from sqlalchemy import select, update

from adh6.storage import db

from ..interfaces.charter_repository import CharterRepository
from .models import Adherent


class CharterSQLRepository(CharterRepository):
    def get(self, charter_id: int, member_id: int) -> datetime | None:
        if charter_id == 1:
            smt = select(Adherent.datesignedminet)
        else:
            smt = select(Adherent.datesignedhosting)
        smt = smt.where(Adherent.id == member_id)
        return db.session.execute(smt).scalar_one_or_none()

    def get_members(self, charter_id: int) -> Tuple[List[int], int]:
        smt = select(Adherent.id)
        if charter_id == 1:
            smt = smt.where(Adherent.datesignedminet)  # type: ignore # TODO: what is the check ?
        else:
            smt = smt.where(Adherent.datesignedhosting)  # type: ignore # TODO: what is the check ?
        r = db.session.execute(smt).scalars().all()
        return r, len(r)  # type: ignore  # TODO: typing is baaaaad

    def update(self, charter_id: int, member_id: int) -> None:
        smt = update(Adherent).where(Adherent.id == member_id)
        if charter_id == 1:
            smt = smt.values(datesignedminet=datetime.now())
        else:
            smt = smt.values(datesignedhosting=datetime.now())
        db.session.execute(smt)
