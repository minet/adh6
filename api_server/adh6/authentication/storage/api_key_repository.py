from typing import List, Tuple, Union
import typing as t
import uuid
from sqlalchemy import select, delete

from adh6.entity import ApiKey
from adh6.storage import db

from ..interfaces import ApiKeyRepository
from .models import ApiKey as SQLApiKey


class ApiKeySQLRepository(ApiKeyRepository):
    def get(self, id: int) -> t.Union[ApiKey, None]:
        smt = select(SQLApiKey).where(SQLApiKey.id == id)
        key = db.session.execute(smt).scalar_one_or_none()
        return self._map_to_api_key(key) if key else None

    def create(self, login: str) -> Tuple[int, str]:
        from hashlib import sha3_512

        session = db.session
        value = str(uuid.uuid4())
        elem = SQLApiKey(
            value=sha3_512(value.encode("utf-8")).hexdigest(),
            user_login=login
        )
        session.add(elem)
        session.commit()

        return elem.id, value

    def delete(self, id: int) -> None:
        smt = delete(SQLApiKey).where(SQLApiKey.id == id)
        db.session.execute(smt)

    def find(self, login: Union[str, None] = None, token_hash: Union[str, None] = None) -> List[ApiKey]:
        smt = select(SQLApiKey)
        if login is not None:
            smt = smt.where(SQLApiKey.user_login == login)
        if token_hash is not None:
            smt = smt.where(SQLApiKey.value == token_hash) 
        return [self._map_to_api_key(i[0]) for i in db.session.execute(smt)]

    def _map_to_api_key(self, api_key: SQLApiKey) -> ApiKey:
        return ApiKey(
            id=api_key.id,
            login=api_key.user_login
        )
