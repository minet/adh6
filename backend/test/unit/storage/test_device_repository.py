from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.device.storage.device_repository import DeviceSQLRepository
from adh6.device.storage.models import Device
from adh6.exceptions import IPAlreadyAssignedError
from sqlalchemy.exc import IntegrityError


class Savepoint:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_info):
        return False


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.get = AsyncMock()
    session.flush = AsyncMock()
    session.begin_nested = Savepoint
    return session


@pytest.fixture
def device_repository(mock_session):
    return DeviceSQLRepository(mock_session)


async def test_set_ip_address_normalizes_address(device_repository, mock_session):
    device = Device(id=1, mac="00-00-00-00-00-01", adherent_id=1, type=0)
    mock_session.get.return_value = device

    result = await device_repository.set_ip_address(1, " 192.0.2.1 ")

    assert device.ip == "192.0.2.1"
    assert result.ipv4_address == "192.0.2.1"
    mock_session.flush.assert_awaited_once_with()


async def test_set_ip_address_can_clear_address(device_repository, mock_session):
    device = Device(id=1, mac="00-00-00-00-00-01", adherent_id=1, type=0, ip="192.0.2.1")
    mock_session.get.return_value = device

    await device_repository.set_ip_address(1, None)

    assert device.ip is None


@pytest.mark.parametrize("ipv4", ["not-an-ip", "2001:db8::1"])
async def test_set_ip_address_rejects_invalid_or_wrong_version(device_repository, mock_session, ipv4):
    mock_session.get.return_value = Device(id=1, mac="00-00-00-00-00-01", adherent_id=1, type=0)

    with pytest.raises(ValueError):
        await device_repository.set_ip_address(1, ipv4)


async def test_set_ip_address_rejects_unknown_device(device_repository, mock_session):
    mock_session.get.return_value = None

    with pytest.raises(ValueError, match="Device 42 not found"):
        await device_repository.set_ip_address(42, None)


async def test_set_ip_address_reports_an_address_taken_by_another_device(device_repository, mock_session):
    mock_session.get.return_value = Device(id=1, mac="00-00-00-00-00-01", adherent_id=1, type=0)
    mock_session.flush.side_effect = IntegrityError("UPDATE devices", {}, Exception("duplicate entry"))

    with pytest.raises(IPAlreadyAssignedError):
        await device_repository.set_ip_address(1, "192.0.2.1")
