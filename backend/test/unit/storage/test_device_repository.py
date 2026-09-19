from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.device.storage.device_repository import DeviceSQLRepository
from adh6.device.storage.models import Device


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.get = AsyncMock()
    session.flush = AsyncMock()
    return session


@pytest.fixture
def device_repository(mock_session):
    return DeviceSQLRepository(mock_session)


async def test_set_ip_addresses_normalizes_addresses(device_repository, mock_session):
    device = Device(id=1, mac="00-00-00-00-00-01", adherent_id=1, type=0)
    mock_session.get.return_value = device

    result = await device_repository.set_ip_addresses(1, " 192.0.2.1 ", "2001:0db8:0:0::1")

    assert device.ip == "192.0.2.1"
    assert device.ipv6 == "2001:db8::1"
    assert result.ipv4_address == "192.0.2.1"
    assert result.ipv6_address == "2001:db8::1"
    mock_session.flush.assert_awaited_once_with()


async def test_set_ip_addresses_can_clear_addresses(device_repository, mock_session):
    device = Device(
        id=1,
        mac="00-00-00-00-00-01",
        adherent_id=1,
        type=0,
        ip="192.0.2.1",
        ipv6="2001:db8::1",
    )
    mock_session.get.return_value = device

    await device_repository.set_ip_addresses(1, None, None)

    assert device.ip is None
    assert device.ipv6 is None


@pytest.mark.parametrize(
    ("ipv4", "ipv6"),
    [
        ("not-an-ip", None),
        ("2001:db8::1", None),
        (None, "192.0.2.1"),
    ],
)
async def test_set_ip_addresses_rejects_invalid_or_wrong_version(device_repository, mock_session, ipv4, ipv6):
    mock_session.get.return_value = Device(id=1, mac="00-00-00-00-00-01", adherent_id=1, type=0)

    with pytest.raises(ValueError):
        await device_repository.set_ip_addresses(1, ipv4, ipv6)


async def test_set_ip_addresses_rejects_unknown_device(device_repository, mock_session):
    mock_session.get.return_value = None

    with pytest.raises(ValueError, match="Device 42 not found"):
        await device_repository.set_ip_addresses(42, None, None)
