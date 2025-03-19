from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text

from adh6.storage import db

from ..interfaces import PingRepository


class PingSQLRepository(PingRepository):
    def ping(self) -> bool:
        try:
            result = db.session.execute(text("SELECT 42 AS result")).fetchall()
            if len(result) != 1:
                return False

        except SQLAlchemyError:
            return False
        else:
            return result == [(42,)]
