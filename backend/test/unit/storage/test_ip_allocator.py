from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.device.storage.ip_allocator import IPSQLAllocator
from adh6.exceptions import BadSubnetError, NoMoreIPAvailableException


@pytest.fixture
def mock_session():
    session = MagicMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = []
    session.execute = AsyncMock(return_value=result)
    return session


@pytest.fixture
def allocator(mock_session):
    return IPSQLAllocator(mock_session)


@pytest.mark.parametrize("subnet", ["", "not-a-subnet", "192.0.2.0/99"])
async def test_available_ip_rejects_invalid_subnets(allocator, subnet):
    with pytest.raises(BadSubnetError):
        await allocator.available_ip(subnet)


async def test_available_ip_skips_reserved_and_used_addresses(allocator, mock_session):
    mock_session.execute.return_value.scalars.return_value.all.return_value = ["192.0.2.2"]

    address = await allocator.available_ip("192.0.2.0/29")

    assert address == "192.0.2.3"


async def test_available_ip_supports_ipv6(allocator, mock_session):
    mock_session.execute.return_value.scalars.return_value.all.return_value = ["2001:db8::2"]

    address = await allocator.available_ip("2001:db8::/126")

    assert address == "2001:db8::3"


async def test_available_ip_raises_when_subnet_is_full(allocator, mock_session):
    mock_session.execute.return_value.scalars.return_value.all.return_value = ["192.0.2.2"]

    with pytest.raises(NoMoreIPAvailableException):
        await allocator.available_ip("192.0.2.0/30")


async def test_available_ip_never_returns_an_excluded_address(allocator):
    address = await allocator.available_ip("192.0.2.0/29", excluded={"192.0.2.2", "192.0.2.3"})

    assert address == "192.0.2.4"
