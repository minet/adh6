from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from adh6.entity import Port, Switch
from adh6.network.snmp.switch_network_manager import SwitchSNMPNetworkManager
from pydantic import SecretStr

_public_community_str = cast(SecretStr, "public")


@pytest.fixture
def mock_repos():
    port_repo = MagicMock()
    switch_repo = MagicMock()
    return port_repo, switch_repo


@pytest.mark.asyncio
async def test_get_port_status(mock_repos):
    port_repo, switch_repo = mock_repos
    manager = SwitchSNMPNetworkManager(port_repo, switch_repo)

    # Mock data
    mock_port = Port(id=1, oid="1.1", switchObj=10, portNumber="Gi1/0/1", room=None)

    mock_switch = Switch(id=10, ip="1.2.3.4", description="Test Switch", community=_public_community_str)

    port_repo.get_by_id = AsyncMock(return_value=mock_port)
    port_repo.get_rcom = AsyncMock(return_value=None)
    switch_repo.get_by_id = AsyncMock(return_value=mock_switch)
    switch_repo.get_community = AsyncMock(return_value="public")

    with patch(
        "adh6.network.snmp.switch_network_manager.get_snmp_value",
        AsyncMock(return_value="up"),
    ) as mock_get:
        status = await manager.get_port_status(1)
        assert status == "up"
        mock_get.assert_called_once_with("public", "1.2.3.4", "IF-MIB", "ifAdminStatus", "1.1")


@pytest.mark.asyncio
async def test_update_port_status_to_down(mock_repos):
    port_repo, switch_repo = mock_repos
    manager = SwitchSNMPNetworkManager(port_repo, switch_repo)

    # Mock data
    mock_port = Port(id=1, oid="1.1", switchObj=10, portNumber="Gi1/0/1", room=None)
    mock_switch = Switch(id=10, ip="1.2.3.4", description="Test Switch", community=_public_community_str)

    port_repo.get_by_id = AsyncMock(return_value=mock_port)
    port_repo.get_rcom = AsyncMock(return_value=None)
    switch_repo.get_by_id = AsyncMock(return_value=mock_switch)
    switch_repo.get_community = AsyncMock(return_value="public")

    with (
        patch(
            "adh6.network.snmp.switch_network_manager.get_snmp_value",
            AsyncMock(return_value="up"),
        ),
        patch(
            "adh6.network.snmp.switch_network_manager.set_snmp_value",
            AsyncMock(return_value="down"),
        ) as mock_set,
    ):
        res = await manager.update_port_status(1)
        assert res == "down"
        mock_set.assert_called_once_with("public", "1.2.3.4", "IF-MIB", "ifAdminStatus", "1.1", 2)


@pytest.mark.asyncio
async def test_update_port_status_to_up(mock_repos):
    port_repo, switch_repo = mock_repos
    manager = SwitchSNMPNetworkManager(port_repo, switch_repo)

    # Mock data
    mock_port = Port(id=1, oid="1.1", switchObj=10, portNumber="Gi1/0/1", room=None)
    mock_switch = Switch(id=10, ip="1.2.3.4", description="Test Switch", community=_public_community_str)

    port_repo.get_by_id = AsyncMock(return_value=mock_port)
    port_repo.get_rcom = AsyncMock(return_value=None)
    switch_repo.get_by_id = AsyncMock(return_value=mock_switch)
    switch_repo.get_community = AsyncMock(return_value="public")

    with (
        patch(
            "adh6.network.snmp.switch_network_manager.get_snmp_value",
            AsyncMock(return_value="down"),
        ),
        patch(
            "adh6.network.snmp.switch_network_manager.set_snmp_value",
            AsyncMock(return_value="up"),
        ) as mock_set,
    ):
        res = await manager.update_port_status(1)
        assert res == "up"
        mock_set.assert_called_once_with("public", "1.2.3.4", "IF-MIB", "ifAdminStatus", "1.1", 1)


@pytest.mark.asyncio
async def test_vlan_methods(mock_repos):
    port_repo, switch_repo = mock_repos
    manager = SwitchSNMPNetworkManager(port_repo, switch_repo)
    mock_port = Port(id=1, oid="1.1", switchObj=10, portNumber="Gi1/0/1", room=None)
    mock_switch = Switch(id=10, ip="1.2.3.4", description="Test Switch", community=_public_community_str)
    port_repo.get_by_id = AsyncMock(return_value=mock_port)
    port_repo.get_rcom = AsyncMock(return_value=None)
    switch_repo.get_by_id = AsyncMock(return_value=mock_switch)
    switch_repo.get_community = AsyncMock(return_value="public")

    with patch(
        "adh6.network.snmp.switch_network_manager.get_snmp_value",
        AsyncMock(return_value=10),
    ) as mock_get:
        vlan = await manager.get_port_vlan(1)
        assert vlan == 10
        mock_get.assert_called_once_with("public", "1.2.3.4", "CISCO-VLAN-MEMBERSHIP-MIB", "vmVlan", "1.1")

    with patch(
        "adh6.network.snmp.switch_network_manager.set_snmp_value",
        AsyncMock(return_value="OK"),
    ) as mock_set:
        res = await manager.update_port_vlan(1, lambda: None, vlan=20)
        assert res == "OK"
        mock_set.assert_called_once_with("public", "1.2.3.4", "CISCO-VLAN-MEMBERSHIP-MIB", "vmVlan", "1.1", 20)


@pytest.mark.asyncio
async def test_mab_methods(mock_repos):
    port_repo, switch_repo = mock_repos
    manager = SwitchSNMPNetworkManager(port_repo, switch_repo)
    mock_port = Port(id=1, oid="1.1", switchObj=10, portNumber="Gi1/0/1", room=None)
    mock_switch = Switch(id=10, ip="1.2.3.4", description="Test Switch", community=_public_community_str)
    port_repo.get_by_id = AsyncMock(return_value=mock_port)
    port_repo.get_rcom = AsyncMock(return_value=None)
    switch_repo.get_by_id = AsyncMock(return_value=mock_switch)
    switch_repo.get_community = AsyncMock(return_value="public")

    with patch(
        "adh6.network.snmp.switch_network_manager.get_snmp_value",
        AsyncMock(return_value="true"),
    ) as mock_get:
        mab = await manager.get_port_mab(1)
        assert mab == "true"
        mock_get.assert_called_once_with("public", "1.2.3.4", "CISCO-MAC-AUTH-BYPASS-MIB", "cmabIfAuthEnabled", "1.1")

    with (
        patch(
            "adh6.network.snmp.switch_network_manager.get_snmp_value",
            AsyncMock(return_value="false"),
        ),
        patch(
            "adh6.network.snmp.switch_network_manager.set_snmp_value",
            AsyncMock(return_value="true"),
        ) as mock_set,
    ):
        res = await manager.update_port_mab(1)
        assert res == "true"
        mock_set.assert_called_once_with(
            "public",
            "1.2.3.4",
            "CISCO-MAC-AUTH-BYPASS-MIB",
            "cmabIfAuthEnabled",
            "1.1",
            1,
        )


@pytest.mark.asyncio
async def test_auth_methods(mock_repos):
    port_repo, switch_repo = mock_repos
    manager = SwitchSNMPNetworkManager(port_repo, switch_repo)
    mock_port = Port(id=1, oid="1.1", switchObj=10, portNumber="Gi1/0/1", room=None)
    mock_switch = Switch(id=10, ip="1.2.3.4", description="Test Switch", community=_public_community_str)
    port_repo.get_by_id = AsyncMock(return_value=mock_port)
    port_repo.get_rcom = AsyncMock(return_value=None)
    switch_repo.get_by_id = AsyncMock(return_value=mock_switch)
    switch_repo.get_community = AsyncMock(return_value="public")

    with patch(
        "adh6.network.snmp.switch_network_manager.get_snmp_value",
        AsyncMock(return_value="auto"),
    ) as mock_get:
        auth = await manager.get_port_auth(1)
        assert auth == "auto"
        mock_get.assert_called_once_with(
            "public",
            "1.2.3.4",
            "IEEE8021-PAE-MIB",
            "dot1xAuthAuthControlledPortControl",
            "1.1",
        )

    # test update_port_auth (auto -> force-unauthorized/3)
    with (
        patch(
            "adh6.network.snmp.switch_network_manager.get_snmp_value",
            AsyncMock(return_value="auto"),
        ),
        patch(
            "adh6.network.snmp.switch_network_manager.set_snmp_value",
            AsyncMock(return_value="force-unauthorized"),
        ) as mock_set,
    ):
        res = await manager.update_port_auth(1)
        assert res == "force-unauthorized"
        mock_set.assert_called_once_with(
            "public",
            "1.2.3.4",
            "IEEE8021-PAE-MIB",
            "dot1xAuthAuthControlledPortControl",
            "1.1",
            3,
        )


@pytest.mark.asyncio
async def test_misc_getters(mock_repos):
    port_repo, switch_repo = mock_repos
    manager = SwitchSNMPNetworkManager(port_repo, switch_repo)
    mock_port = Port(id=1, oid="1.1", switchObj=10, portNumber="Gi1/0/1", room=None)
    mock_switch = Switch(id=10, ip="1.2.3.4", description="Test Switch", community=_public_community_str)
    port_repo.get_by_id = AsyncMock(return_value=mock_port)
    port_repo.get_rcom = AsyncMock(return_value=None)
    switch_repo.get_by_id = AsyncMock(return_value=mock_switch)
    switch_repo.get_community = AsyncMock(return_value="public")

    with patch(
        "adh6.network.snmp.switch_network_manager.get_snmp_value",
        AsyncMock(return_value="authenticated"),
    ) as _:
        use = await manager.get_port_use(1)
        assert use == "authenticated"

    with patch(
        "adh6.network.snmp.switch_network_manager.get_snmp_value",
        AsyncMock(return_value=1000000000),
    ) as _:
        speed = await manager.get_port_speed(1)
        assert speed == 1000000000

    with patch(
        "adh6.network.snmp.switch_network_manager.get_snmp_value",
        AsyncMock(return_value="My Alias"),
    ) as _:
        alias = await manager.get_port_alias(1)
        assert alias == "My Alias"


@pytest.mark.asyncio
async def test_update_port_alias(mock_repos):
    port_repo, switch_repo = mock_repos
    manager = SwitchSNMPNetworkManager(port_repo, switch_repo)
    mock_port = Port(id=1, oid="1.1", switchObj=10, portNumber="Gi1/0/1", room=None)
    mock_switch = Switch(id=10, ip="1.2.3.4", description="Test Switch", community=_public_community_str)
    port_repo.get_by_id = AsyncMock(return_value=mock_port)
    port_repo.get_rcom = AsyncMock(return_value=None)
    switch_repo.get_by_id = AsyncMock(return_value=mock_switch)
    switch_repo.get_community = AsyncMock(return_value="public")

    with patch(
        "adh6.network.snmp.switch_network_manager.set_snmp_value",
        AsyncMock(return_value="New Alias"),
    ) as mock_set:
        res = await manager.update_port_alias(1, "New Alias")
        assert res == "New Alias"
        # We check that it's called with OctetString
        args, kwargs = mock_set.call_args
        from pysnmp.proto.rfc1902 import OctetString

        assert isinstance(args[5], OctetString)
        assert str(args[5]) == "New Alias"


@pytest.mark.asyncio
async def test_ping_from_switch_success(mock_repos):
    port_repo, switch_repo = mock_repos
    manager = SwitchSNMPNetworkManager(port_repo, switch_repo)
    mock_switch = Switch(id=10, ip="1.2.3.4", description="Test Switch", community=_public_community_str)
    switch_repo.get_by_id = AsyncMock(return_value=mock_switch)
    switch_repo.get_community = AsyncMock(return_value="public")

    # Mock SNMP responses:
    # 1. poll completed (.14) -> "1"
    # 2. get sent (.9) -> "5"
    # 3. get received (.10) -> "5"
    # 4. get min (.11) -> "10"
    # 5. get avg (.12) -> "12"
    # 6. get max (.13) -> "15"
    snmp_get_responses = ["1", "5", "5", "10", "12", "15"]

    with (
        patch(
            "adh6.network.snmp.switch_network_manager.set_snmp_values_raw",
            AsyncMock(return_value=None),
        ) as mock_set_raw,
        patch(
            "adh6.network.snmp.switch_network_manager.get_snmp_value_raw",
            AsyncMock(side_effect=snmp_get_responses),
        ) as _,
        patch("asyncio.sleep", AsyncMock(return_value=None)),
    ):
        result = await manager.ping_from_switch(10, "8.8.8.8", count=5, timeout_ms=1000, size=64)

        assert result["sent"] == 5
        assert result["received"] == 5
        assert result["minRtt"] == 10
        assert result["avgRtt"] == 12
        assert result["maxRtt"] == 15

        # Verify initial SET call OIDs and values
        # BASE = 1.3.6.1.4.1.9.9.16.1.1.1
        # .2 = protocol(1), .3 = addr, .4 = count(5), .5 = size(64), .6 = timeout(1000), .15 = owner, .16 = status(4)
        args, kwargs = mock_set_raw.call_args_list[0]
        oid_values = args[2]
        oids = [ov[0] for ov in oid_values]
        assert any(".2." in o for o in oids)
        assert any(".3." in o for o in oids)
        assert any(".4." in o for o in oids)
        assert any(".5." in o for o in oids)
        assert any(".6." in o for o in oids)
        assert any(".15." in o for o in oids)
        assert any(".16." in o for o in oids)

        # Verify cleanup SET call (destroy=6)
        args_cleanup, _ = mock_set_raw.call_args_list[1]
        assert args_cleanup[2][0][1] == 6


@pytest.mark.asyncio
async def test_discover_ports(mock_repos):
    port_repo, switch_repo = mock_repos
    manager = SwitchSNMPNetworkManager(port_repo, switch_repo)
    mock_switch = Switch(id=10, ip="1.2.3.4", description="Test Switch", community=_public_community_str)
    switch_repo.get_by_id = AsyncMock(return_value=mock_switch)
    switch_repo.get_community = AsyncMock(return_value="public")

    walk_results = [
        ("10101", "GigabitEthernet1/0/1"),
        ("10102", "GigabitEthernet1/0/2"),
    ]

    with patch(
        "adh6.network.snmp.switch_network_manager.walk_snmp",
        AsyncMock(return_value=walk_results),
    ) as mock_walk:
        ports = await manager.discover_ports(10)
        assert len(ports) == 2
        assert ports[0]["portNumber"] == "GigabitEthernet1/0/1"
        assert ports[0]["oid"] == "10101"
        mock_walk.assert_called_once_with("public", "1.2.3.4", "IF-MIB", "ifDescr")


@pytest.mark.asyncio
async def test_sync_port_names(mock_repos):
    port_repo, switch_repo = mock_repos
    manager = SwitchSNMPNetworkManager(port_repo, switch_repo)
    mock_switch = Switch(id=10, ip="1.2.3.4", description="Test Switch", community=_public_community_str)
    switch_repo.get_by_id = AsyncMock(return_value=mock_switch)
    switch_repo.get_community = AsyncMock(return_value="public")

    # DB has 1 port with OID 10101, but name is currently "OldName"
    existing_port = Port(id=1, oid="10101", portNumber="OldName", switchObj=10, room=None)
    port_repo.search_by = AsyncMock(return_value=([existing_port], 1))
    port_repo.update = AsyncMock(return_value=None)

    walk_results = [("10101", "NewName-Gi1/0/1"), ("10102", "OtherPort")]

    with patch(
        "adh6.network.snmp.switch_network_manager.walk_snmp",
        AsyncMock(return_value=walk_results),
    ):
        res = await manager.sync_port_names(10)
        assert res["success"] == 1
        assert res["failed"] == 0
        # Verify repo update was called with new name
        args, _ = port_repo.update.call_args
        assert args[0].port_number == "NewName-Gi1/0/1"
        assert args[0].id == 1
