import asyncio

import pytest
from adh6.entity import AbstractPort
from adh6.exceptions import (
    PortAlreadyExists,
    PortAssignmentConflict,
    PortNotFoundError,
    RoomNotFoundError,
    ValidationError,
)
from adh6.network.port_manager import PortManager
from adh6.network.storage.models import Port as SQLPort, Switch
from adh6.network.storage.port_repository import PortSQLRepository
from adh6.room.storage.models import Chambre
from adh6.storage.sql.models import Base
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


@pytest.fixture
async def sessions(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/ports.db")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
    async with factory.begin() as session:
        session.add_all([Switch(id=1), Switch(id=2), Chambre(id=1, numero=101), Chambre(id=2, numero=102)])
    yield factory
    await engine.dispose()


def new_port(oid="10101", switch=1, room=None):
    return AbstractPort(portNumber="GigabitEthernet1/0/1", oid=oid, switchObj=switch, room=room)


async def test_duplicate_and_canonical_oid(sessions):
    async with sessions.begin() as session:
        repo = PortSQLRepository(session)
        port = await PortManager(repo).create(new_port(" 0010101 "))
        assert port.oid == "10101"
        with pytest.raises(PortAlreadyExists):
            await PortManager(repo).create(new_port())
        other = await PortManager(repo).create(new_port(switch=2))
        assert other.switch_obj == 2
    async with sessions() as session:
        assert await session.scalar(select(func.count()).select_from(SQLPort)) == 2


@pytest.mark.parametrize("oid", [None, "", "Gi1/0/1", "1.2.3", "0", "-1", "2147483648", "\uff11\uff12"])
async def test_invalid_oid_does_not_create_a_port(sessions, oid):
    async with sessions.begin() as session:
        with pytest.raises(ValidationError):
            await PortManager(PortSQLRepository(session)).create(new_port(oid))
        assert await session.scalar(select(func.count()).select_from(SQLPort)) == 0


async def test_concurrent_creation_creates_only_one_port(sessions):
    ready = asyncio.Event()

    async def create():
        await ready.wait()
        try:
            async with sessions.begin() as session:
                await PortManager(PortSQLRepository(session)).create(new_port())
        except PortAlreadyExists:
            return "duplicate"
        else:
            return "created"

    tasks = [asyncio.create_task(create()) for _ in range(2)]
    ready.set()
    assert sorted(await asyncio.gather(*tasks)) == ["created", "duplicate"]
    async with sessions() as session:
        assert await session.scalar(select(func.count()).select_from(SQLPort)) == 1


async def test_existing_duplicates_remain_and_do_not_allow_a_third(sessions):
    async with sessions.begin() as session:
        session.add_all(
            [SQLPort(numero="old", oid="0010101", switch_id=1), SQLPort(numero="old", oid="10101", switch_id=1)]
        )
    async with sessions.begin() as session:
        with pytest.raises(PortAlreadyExists):
            await PortManager(PortSQLRepository(session)).create(new_port())
    async with sessions() as session:
        assert await session.scalar(select(func.count()).select_from(SQLPort)) == 2


async def test_identity_update_cannot_create_duplicate(sessions):
    async with sessions.begin() as session:
        repo = PortSQLRepository(session)
        await PortManager(repo).create(new_port())
        second = await PortManager(repo).create(new_port("10102"))
        assert second.id is not None
        with pytest.raises(PortAlreadyExists):
            await repo.update(AbstractPort(id=second.id, oid="10101"))
        with pytest.raises(ValidationError):
            await PortManager(repo).update(second.id, AbstractPort(oid="Gi1/0/1"))
        assert (await repo.get_by_id(second.id)).oid == "10102"


async def test_assignment_preserves_port_identity_and_public_access(sessions):
    async with sessions.begin() as session:
        repo = PortSQLRepository(session)
        port = await PortManager(repo).create(new_port())
        assert port.id is not None
        await repo.update(AbstractPort(id=port.id, publiclyAccessible=True))
        assigned = await repo.assign_room(port.id, 1, None)
        assert assigned.room == 1
        assert assigned.room_obj is not None
        assert assigned.room_obj.room_number == 101
        transferred = await repo.assign_room(port.id, 2, 1)
        assert transferred.room == 2
        assert transferred.oid == port.oid
        assert transferred.port_number == port.port_number
        assert transferred.publicly_accessible is True
        # Repeating a successful transfer is idempotent.
        assert (await repo.assign_room(port.id, 2, 1)).room == 2
        with pytest.raises(PortAssignmentConflict):
            await repo.assign_room(port.id, 1, None)
        assert (await repo.get_by_id(port.id)).room == 2
        with pytest.raises(RoomNotFoundError):
            await repo.assign_room(port.id, 999, 2)
        with pytest.raises(PortNotFoundError):
            await repo.assign_room(999, 1, None)


async def test_detach_preserves_inventory_and_rejects_stale_room(sessions):
    async with sessions.begin() as session:
        repo = PortSQLRepository(session)
        port = await PortManager(repo).create(new_port(room=1))
        assert port.id is not None
        detached = await repo.assign_room(port.id, None, 1)
        assert detached.room is None
        assert detached.room_obj is None
        assert detached.switch_obj == 1
        assert detached.oid == "10101"
        assert (await repo.get_by_id(port.id)).id == port.id
        assert (await repo.assign_room(port.id, None, 1)).room is None
        await repo.assign_room(port.id, 2, None)
        with pytest.raises(PortAssignmentConflict):
            await repo.assign_room(port.id, None, 1)
        assert (await repo.get_by_id(port.id)).room == 2
