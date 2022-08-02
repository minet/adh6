from datetime import datetime
from typing import List, Tuple, Union

from sqlalchemy import select, update
from sqlalchemy.orm import Session
from adh6.constants import CTX_SQL_SESSION
from adh6.member.interfaces.charter_repository import CharterRepository
from adh6.storage.sql.models import Adherent


class CharterSQLRepository(CharterRepository):
    def get(self, ctx, charter_id: int, member_id: int) -> Union[datetime, None]:
        session: Session = ctx.get(CTX_SQL_SESSION)
        if charter_id == 1:
            smt = select(Adherent.datesignedminet)
        else:
            smt = select(Adherent.datesignedhosting)
        smt = smt.where(Adherent.id == member_id)
        return session.execute(smt).scalar_one_or_none()

    def get_members(self, ctx, charter_id: int) -> Tuple[List[int], int]:
        session: Session = ctx.get(CTX_SQL_SESSION)
        smt = select(Adherent.id)
        if charter_id == 1:
            smt = smt.where(Adherent.datesignedminet)
        else:
            smt = smt.where(Adherent.datesignedhosting)
        r = session.execute(smt).scalars().all()
        return r, len(r)

    def update(self, ctx, charter_id: int, member_id: int) -> None:
        session: Session = ctx.get(CTX_SQL_SESSION)
        smt = update(Adherent).where(Adherent.id == member_id)
        if charter_id == 1:
            smt = smt.values(datesignedminet=datetime.now())
        else:
            smt = smt.values(datesignedhosting=datetime.now())
        session.execute(smt)
