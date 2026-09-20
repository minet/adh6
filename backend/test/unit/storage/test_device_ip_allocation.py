from collections.abc import Collection
from ipaddress import ip_network
from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.device.device_ip_manager import MAX_ALLOCATION_ATTEMPTS, DeviceIpManager
from adh6.device.interfaces import IpAllocator
from adh6.device.storage.device_repository import DeviceSQLRepository, DeviceType
from adh6.device.storage.models import Device
from adh6.exceptions import IPAlreadyAssignedError
from adh6.storage.sql.models import Base
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

VLAN = MagicMock(ipv4_network="192.0.2.0/29", ipv6_network=None)


def wired_device(device_id: int):
    return MagicMock(id=device_id, connection_type=DeviceType.wired.name)


class SnapshotAllocator(IpAllocator):
    def __init__(self, used: Collection[str]):
        self.used = set(used)

    async def available_ip(
        self,
        ip_range: str,
        member_id: int | None = None,
        reserved_hosts: int = 1,
        excluded: Collection[str] = (),
    ) -> str:
        hosts = list(ip_network(ip_range).hosts())[reserved_hosts:]
        return next(str(host) for host in hosts if str(host) not in self.used | set(excluded))


@pytest.fixture
async def sessions(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/devices.db")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
    async with factory.begin() as session:
        session.add_all(
            [
                Device(id=1, mac="00-00-00-00-00-01", adherent_id=1, type=0, ip="192.0.2.2"),
                Device(id=2, mac="00-00-00-00-00-02", adherent_id=2, type=0),
                Device(id=3, mac="00-00-00-00-00-03", adherent_id=3, type=0),
            ]
        )
    yield factory
    await engine.dispose()


async def test_losing_a_race_for_an_address_takes_the_next_free_one(sessions):
    async with sessions.begin() as session:
        # Another request has just taken 192.0.2.2, which this one still sees as free.
        manager = DeviceIpManager(SnapshotAllocator(used=[]), DeviceSQLRepository(session), MagicMock())
        session.add(Device(id=4, mac="00-00-00-00-00-04", adherent_id=4, type=0))
        await session.flush()

        await manager.allocate_ip_with_vlan(device=wired_device(2), member=MagicMock(), vlan=VLAN)

    async with sessions() as session:
        addresses = dict((await session.execute(select(Device.id, Device.ip))).all())
    assert addresses[1] == "192.0.2.2"
    assert addresses[2] == "192.0.2.3"
    assert 4 in addresses


async def test_allocation_gives_up_when_every_attempt_loses(sessions):
    repository = MagicMock()
    repository.set_ip_addresses = AsyncMock(side_effect=IPAlreadyAssignedError)
    manager = DeviceIpManager(SnapshotAllocator(used=[]), repository, MagicMock())

    with pytest.raises(IPAlreadyAssignedError):
        await manager.allocate_ip_with_vlan(device=wired_device(2), member=MagicMock(), vlan=VLAN)

    assert repository.set_ip_addresses.await_count == MAX_ALLOCATION_ATTEMPTS
    tried = [call.args[1] for call in repository.set_ip_addresses.await_args_list]
    assert len(set(tried)) == MAX_ALLOCATION_ATTEMPTS
