import uuid
from hashlib import sha3_512

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.entity import ApiKey

from ..interfaces import ApiKeyRepository
from .models import ApiKey as SQLApiKey


class ApiKeySQLRepository(ApiKeyRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: int) -> ApiKey | None:
        stmt = select(SQLApiKey).where(SQLApiKey.id == id)
        key = await self.session.scalar(stmt)
        return self._map_to_api_key(key) if key else None

    async def create(self, login: str) -> tuple[int, str]:
        value = str(uuid.uuid4())
        elem = SQLApiKey(value=sha3_512(value.encode("utf-8")).hexdigest(), user_login=login)
        self.session.add(elem)
        await self.session.flush()
        return elem.id, value

    async def delete(self, id: int) -> None:
        smt = delete(SQLApiKey).where(SQLApiKey.id == id)
        await self.session.execute(smt)

    async def find(self, login: str | None = None, token_hash: str | None = None) -> list[ApiKey]:
        stmt = select(SQLApiKey)
        if login is not None:
            stmt = stmt.where(SQLApiKey.user_login == login)
        if token_hash is not None:
            stmt = stmt.where(SQLApiKey.value == token_hash)

        result = (await self.session.execute(stmt)).all()
        return [self._map_to_api_key(i[0]) for i in result]

    def _map_to_api_key(self, api_key: SQLApiKey) -> ApiKey:
        return ApiKey(id=api_key.id, login=api_key.user_login)
