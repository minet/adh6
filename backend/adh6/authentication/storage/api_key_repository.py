import uuid
from hashlib import sha3_512

from sqlalchemy import delete, select

from adh6.entity import ApiKey
from adh6.storage import db

from ..interfaces import ApiKeyRepository
from .models import ApiKey as SQLApiKey


class ApiKeySQLRepository(ApiKeyRepository):
    def get(self, id: int) -> ApiKey | None:
        stmt = select(SQLApiKey).where(SQLApiKey.id == id)
        with db.sessionmaker.begin() as session:
            key = session.execute(stmt).scalar_one_or_none()
            return self._map_to_api_key(key) if key else None

    def create(self, login: str) -> tuple[int, str]:
        value = str(uuid.uuid4())
        elem = SQLApiKey(value=sha3_512(value.encode("utf-8")).hexdigest(), user_login=login)
        with db.sessionmaker.begin() as session:
            session.add(elem)
            session.flush()
            elem_id = elem.id

        return elem_id, value

    def delete(self, id: int) -> None:
        smt = delete(SQLApiKey).where(SQLApiKey.id == id)
        with db.sessionmaker.begin() as session:
            session.execute(smt)

    def find(self, login: str | None = None, token_hash: str | None = None) -> list[ApiKey]:
        stmt = select(SQLApiKey)
        if login is not None:
            stmt = stmt.where(SQLApiKey.user_login == login)
        if token_hash is not None:
            stmt = stmt.where(SQLApiKey.value == token_hash)

        with db.sessionmaker.begin() as session:
            result = session.execute(stmt).all()
            return [self._map_to_api_key(i[0]) for i in result]

    def _map_to_api_key(self, api_key: SQLApiKey) -> ApiKey:
        return ApiKey(id=api_key.id, login=api_key.user_login)
