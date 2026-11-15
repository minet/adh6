import json

import httpx
import pytest
from adh6 import database
from adh6.config.configuration import settings
from adh6.device.storage.models import Device
from adh6.kea import sync
from adh6.kea.client import KeaClient
from adh6.kea.tracker import mark_member
from adh6.member.storage.models import Adherent
from adh6.room.storage.models import Chambre
from adh6.storage.sql.models import Base
from adh6.subnet.storage.models import Vlan
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


@pytest.fixture
async def sessions(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/sync.db")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
    async with factory.begin() as session:
        session.add_all(
            [
                Vlan(id=1, numero=41),
                Chambre(id=10, numero=1001, vlan_id=1),
                Adherent(id=1, login="one", chambre_id=10),
                Device(id=1, mac="AA-BB-CC-DD-EE-01", adherent_id=1, type=0, ip="157.159.41.10"),
            ]
        )
    yield factory
    await engine.dispose()


@pytest.fixture
def kea(monkeypatch):
    """Enable the Kea sync against a fake Kea that holds a stale reservation for the device."""
    monkeypatch.setattr(settings, "kea_enabled", True)
    monkeypatch.setattr(settings, "kea_api_urls", "https://kea1:8443/")
    monkeypatch.setattr(settings, "kea_api_password", SecretStr("secret"))
    commands: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        commands.append(body)
        if body["command"] == "reservation-get-by-id":
            host = {"subnet-id": 41, "hw-address": "aa:bb:cc:dd:ee:01", "ip-address": "157.159.41.99"}
            return httpx.Response(200, json=[{"result": 0, "arguments": {"hosts": [host]}}])
        return httpx.Response(200, json=[{"result": 0, "text": "ok"}])

    monkeypatch.setattr(sync, "KeaClient", lambda config: KeaClient(config, transport=httpx.MockTransport(handler)))
    return commands


async def test_sync_after_commit_fixes_the_marked_member(sessions, kea):
    async with sessions() as session:
        mark_member(session, 1)
        await sync.sync_after_commit(session)

    assert [c["command"] for c in kea] == ["reservation-get-by-id", "reservation-del", "reservation-add"]
    assert kea[2]["arguments"]["reservation"]["ip-address"] == "157.159.41.10"


async def test_sync_does_nothing_when_disabled(sessions, kea, monkeypatch):
    monkeypatch.setattr(settings, "kea_enabled", False)
    async with sessions() as session:
        mark_member(session, 1)
        await sync.sync_after_commit(session)
        # The marks are dropped anyway: they must not leak into a later commit.
        assert "kea_member_ids" not in session.info

    assert kea == []


async def test_sync_never_raises(sessions, monkeypatch):
    monkeypatch.setattr(settings, "kea_enabled", True)
    monkeypatch.setattr(settings, "kea_api_urls", "https://kea1:8443/")
    monkeypatch.setattr(settings, "kea_api_password", SecretStr("secret"))

    def down(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("down", request=request)

    monkeypatch.setattr(sync, "KeaClient", lambda config: KeaClient(config, transport=httpx.MockTransport(down)))
    async with sessions() as session:
        mark_member(session, 1)
        await sync.sync_after_commit(session)  # logs a warning, does not raise


async def test_get_session_syncs_only_after_a_commit(sessions, monkeypatch):
    synced: list[object] = []

    async def fake_sync(session):
        synced.append(session)

    monkeypatch.setattr(database, "async_session_factory", sessions)
    monkeypatch.setattr(database, "sync_after_commit", fake_sync)

    committed = database.get_session()
    await committed.__anext__()
    with pytest.raises(StopAsyncIteration):
        await committed.__anext__()
    assert len(synced) == 1

    rolled_back = database.get_session()
    await rolled_back.__anext__()
    with pytest.raises(ValueError):
        await rolled_back.athrow(ValueError("handler failed"))
    assert len(synced) == 1
