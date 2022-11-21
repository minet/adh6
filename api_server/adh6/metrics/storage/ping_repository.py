from sqlalchemy.exc import SQLAlchemyError
from adh6.storage import session

from ..interfaces import PingRepository


class PingSQLRepository(PingRepository):
    def ping(self) -> bool:
        try:
            result = session.execute('SELECT 42 AS result').fetchall()
            if 1 != len(result):
                return False

            return [(42,)] == result

        except SQLAlchemyError:
            return False
