from datetime import datetime
from typing import List, Tuple, Union

from sqlalchemy import select, update
from adh6.storage import session

from .models import Adherent
from ..interfaces.charter_repository import CharterRepository


class CharterSQLRepository(CharterRepository):
    def get(self, charter_id: int, member_id: int) -> Union[datetime, None]:
        if charter_id == 1:
            smt = select(Adherent.datesignedminet)
        else:
            smt = select(Adherent.datesignedhosting)
        smt = smt.where(Adherent.id == member_id)
        return session.execute(smt).scalar_one_or_none()

    def get_members(self, charter_id: int) -> Tuple[List[int], int]:
        smt = select(Adherent.id)
        if charter_id == 1:
            smt = smt.where(Adherent.datesignedminet)
        else:
            smt = smt.where(Adherent.datesignedhosting)
        r = session.execute(smt).scalars().all()
        return r, len(r)

    def update(self, charter_id: int, member_id: int) -> None:
        smt = update(Adherent).where(Adherent.id == member_id)
        if charter_id == 1:
            smt = smt.values(datesignedminet=datetime.now())
        else:
            smt = smt.values(datesignedhosting=datetime.now())
        session.execute(smt)
