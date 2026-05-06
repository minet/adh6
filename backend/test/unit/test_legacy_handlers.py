"""Tests for legacy HTTP handler classes to increase code coverage.

These handlers use @with_context (sync wrapper around async methods) and are
legacy code not connected to the current FastAPI routes. We test their method
bodies directly via inspect.unwrap to ensure coverage.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from adh6.authentication.enums import Roles
from adh6.entity import Member
from pytest import fixture


def unwrap(bound_method):
    """Unwrap all decorators to get the original async function."""
    func = getattr(bound_method, "__func__", bound_method)
    while hasattr(func, "__wrapped__"):
        func = func.__wrapped__
    return func


@fixture(autouse=True)
def ctx(faker, monkeypatch):
    """Setup context with admin user roles."""
    import adh6.context as context

    context.set_user(28)
    context.set_roles(
        [
            Roles.USER.value,
            Roles.ADMIN_READ.value,
            Roles.ADMIN_WRITE.value,
            Roles.TRESO_READ.value,
            Roles.TRESO_WRITE.value,
            Roles.NETWORK_READ.value,
            Roles.NETWORK_WRITE.value,
        ]
    )


@fixture
def sample_member(faker) -> Member:
    return Member(
        id=28,
        username=faker.user_name(),
        email=faker.email(),
        firstName=faker.first_name(),
        lastName=faker.last_name(),
        departureDate=datetime(2099, 1, 1),
    )


# ===========================================================================
# MemberHandler tests
# ===========================================================================
class TestMemberHandler:
    @fixture
    def mock_member_manager(self):
        from adh6.member.member_manager import MemberManager

        return MagicMock(spec=MemberManager)

    @fixture
    def mock_charter_manager(self):
        from adh6.member.charter_manager import CharterManager

        return MagicMock(spec=CharterManager)

    @fixture
    def mock_subscription_manager(self):
        from adh6.member.subscription_manager import SubscriptionManager

        return MagicMock(spec=SubscriptionManager)

    @fixture
    def handler(self, mock_member_manager, mock_charter_manager, mock_subscription_manager):
        from adh6.member.http.member import MemberHandler

        return MemberHandler(
            member_manager=mock_member_manager,
            charter_manager=mock_charter_manager,
            subscription_manager=mock_subscription_manager,
        )

    async def test_search(self, handler, mock_member_manager, sample_member):
        mock_member_manager.search = AsyncMock(return_value=([sample_member.id], 1))
        result, status, headers = await unwrap(handler.search)(handler, limit=10, offset=0)
        assert status == 200
        assert "X-Total-Count" in headers

    async def test_get_happy_path(self, handler, mock_member_manager, sample_member):
        mock_member_manager.get_by_id = AsyncMock(return_value=sample_member)
        result, status = await unwrap(handler.get)(handler, id_=28)
        assert status == 200

    async def test_post(self, handler, mock_member_manager, sample_member, faker):
        mock_member_manager.create = AsyncMock(return_value=sample_member)
        body = {
            "username": faker.user_name(),
            "firstName": faker.first_name(),
            "lastName": faker.last_name(),
            "mail": faker.email(),
        }
        result, status = await unwrap(handler.post)(handler, body=body)
        assert status == 201

    async def test_patch(self, handler, mock_member_manager, sample_member, faker):
        mock_member_manager.update = AsyncMock(return_value=None)
        body = {"username": faker.user_name(), "mail": faker.email()}
        result, status = await unwrap(handler.patch)(handler, id_=sample_member.id, body=body)
        assert status == 204

    async def test_password_put_happy_path(self, handler, mock_member_manager, sample_member):
        mock_member_manager.change_password = AsyncMock(return_value=True)
        result, status = await unwrap(handler.password_put)(
            handler, id_=sample_member.id, body={"password": "NewPass1!", "hashedPassword": None}
        )
        assert status == 204

    async def test_logs_search(self, handler, mock_member_manager, sample_member):
        mock_member_manager.get_logs = AsyncMock(return_value={"logs": [], "total": 0, "hasMore": False})
        result, status = await unwrap(handler.logs_search)(handler, id_=sample_member.id)
        assert status == 200

    async def test_statuses_search(self, handler, mock_member_manager, sample_member):
        mock_member_manager.get_statuses = AsyncMock(return_value=[])
        result, status = await unwrap(handler.statuses_search)(handler, id_=sample_member.id)
        assert status == 200

    async def test_subscription_post(self, handler, mock_subscription_manager, sample_member, faker):
        from adh6.constants import MembershipStatus
        from adh6.entity import AbstractMembership

        membership = AbstractMembership(
            uuid=faker.uuid4(), member=sample_member.id, status=MembershipStatus.INITIAL.value
        )
        mock_subscription_manager.create = AsyncMock(return_value=membership)
        body = {"member": sample_member.id}
        result, status = await unwrap(handler.subscription_post)(handler, id_=sample_member.id, body=body)
        assert status == 200

    async def test_subscription_patch(self, handler, mock_subscription_manager, sample_member):
        mock_subscription_manager.update = AsyncMock(return_value=None)
        body = {"member": sample_member.id}
        result, status = await unwrap(handler.subscription_patch)(handler, id_=sample_member.id, body=body)
        assert status == 204

    async def test_subscription_validate(self, handler, mock_subscription_manager, mock_member_manager, sample_member):
        mock_subscription_manager.validate = AsyncMock(return_value=None)
        mock_member_manager.update_subnet = AsyncMock(return_value=None)
        result, status = await unwrap(handler.subscription_validate)(handler, id_=sample_member.id)
        assert status == 204

    async def test_charter_get(self, handler, mock_charter_manager, sample_member):
        mock_charter_manager.get = AsyncMock(return_value=None)
        result, status = await unwrap(handler.charter_get)(handler, id_=sample_member.id, charter_id=1)
        assert status == 200

    async def test_charter_put(self, handler, mock_charter_manager, sample_member):
        mock_charter_manager.sign = AsyncMock(return_value=None)
        result, status = await unwrap(handler.charter_put)(handler, id_=sample_member.id, charter_id=1)
        assert status == 204

    async def test_comment_put(self, handler, mock_member_manager, sample_member):
        mock_member_manager.change_comment = AsyncMock(return_value=None)
        body = {"comment": "Test comment"}
        result, status = await unwrap(handler.comment_put)(handler, id_=sample_member.id, body=body)
        assert status == 204

    async def test_comment_search(self, handler, mock_member_manager, sample_member):
        from adh6.entity import Comment

        mock_member_manager.get_comment = AsyncMock(return_value=Comment(comment="Test"))
        result, status = await unwrap(handler.comment_search)(handler, id_=sample_member.id)
        assert status == 200


# ===========================================================================
# DeviceHandler tests
# ===========================================================================
class TestDeviceHandler:
    @fixture
    def mock_device_manager(self):
        from adh6.device.device_manager import DeviceManager

        return MagicMock(spec=DeviceManager)

    @fixture
    def handler(self, mock_device_manager):
        from adh6.device.http.device import DeviceHandler

        return DeviceHandler(device_manager=mock_device_manager)

    @fixture
    def sample_device(self, faker, sample_member):
        from adh6.entity import Device

        return Device(
            id=faker.random_digit_not_null(),
            mac=faker.mac_address().replace(":", "-").upper(),
            member=sample_member.id,
            connectionType="wired",
        )

    async def test_search_admin(self, handler, mock_device_manager, sample_device):
        mock_device_manager.search = AsyncMock(return_value=([sample_device], 1))
        result, status, headers = await unwrap(handler.search)(handler, limit=10, offset=0, filter_={"member": 28})
        assert status == 200

    async def test_get_happy_path(self, handler, mock_device_manager, sample_device):
        mock_device_manager.get_by_id = AsyncMock(return_value=sample_device)
        result, status = await unwrap(handler.get)(handler, id_=sample_device.id)
        assert status == 200

    async def test_post(self, handler, mock_device_manager, sample_device, faker):
        mock_device_manager.create = AsyncMock(return_value=sample_device)
        body = {"mac": "00-11-22-33-44-55", "connectionType": "wired", "member": 28}
        result, status = await unwrap(handler.post)(handler, body=body)
        assert status == 201

    async def test_delete(self, handler, mock_device_manager, sample_device):
        mock_device_manager.get_owner = AsyncMock(return_value=28)
        mock_device_manager.delete = AsyncMock(return_value=None)
        result, status = await unwrap(handler.delete)(handler, id_=sample_device.id)
        assert status == 204

    async def test_vendor_search(self, handler, mock_device_manager, sample_device):
        mock_device_manager.get_by_id = AsyncMock(return_value=sample_device)
        mock_device_manager.get_mac_vendor = AsyncMock(return_value="TestVendor")
        result, status = await unwrap(handler.vendor_search)(handler, id_=sample_device.id)
        assert status == 200
        assert result == "TestVendor"

    async def test_mab_search(self, handler, mock_device_manager, sample_device):
        mock_device_manager.get_mab = AsyncMock(return_value=False)
        result, status = await unwrap(handler.mab_search)(handler, id_=sample_device.id)
        assert status == 200

    async def test_mab_post(self, handler, mock_device_manager, sample_device):
        mock_device_manager.put_mab = AsyncMock(return_value=True)
        result, status = await unwrap(handler.mab_post)(handler, id_=sample_device.id)
        assert status == 200

    async def test_member_search(self, handler, mock_device_manager, sample_device):
        mock_device_manager.get_owner = AsyncMock(return_value=28)
        result, status = await unwrap(handler.member_search)(handler, id_=sample_device.id)
        assert status == 200
        assert result == 28


# ===========================================================================
# RoomHandler tests
# ===========================================================================
class TestRoomHandler:
    @fixture
    def mock_room_manager(self):
        from adh6.room.room_manager import RoomManager

        return MagicMock(spec=RoomManager)

    @fixture
    def handler(self, mock_room_manager):
        from adh6.room.http.room import RoomHandler

        return RoomHandler(room_manager=mock_room_manager)

    @fixture
    def sample_room(self, faker):
        from adh6.entity import Room

        return Room(id=faker.random_digit_not_null(), roomNumber=100, vlan=41, description="Test room")

    async def test_get(self, handler, mock_room_manager, sample_room):
        mock_room_manager.get_by_id = AsyncMock(return_value=sample_room)
        result, status = await unwrap(handler.get)(handler, id_=sample_room.id)
        assert status == 200

    async def test_member_search(self, handler, mock_room_manager, sample_room):
        mock_room_manager.list_members = AsyncMock(return_value=[1, 2])
        result, status = await unwrap(handler.member_search)(handler, id_=sample_room.id)
        assert status == 200
        assert result == [1, 2]

    async def test_member_post(self, handler, mock_room_manager, sample_room):
        mock_room_manager.add_member = AsyncMock(return_value=None)
        result, status = await unwrap(handler.member_post)(handler, id_=sample_room.id, body={"id": 1})
        assert status == 204

    async def test_member_delete(self, handler, mock_room_manager, sample_room):
        mock_room_manager.remove_member = AsyncMock(return_value=None)
        result, status = await unwrap(handler.member_delete)(handler, id_=sample_room.id, member_id=1)
        assert status == 204

    async def test_member_add_patch(self, handler, mock_room_manager, sample_room):
        mock_room_manager.add_member = AsyncMock(return_value=None)
        # member_add_patch calls self.member_post internally (decorated, not awaitable directly)
        # patch it to an awaitable to bypass broken decorator
        handler.member_post = AsyncMock(return_value=(None, 204))
        result, status = await unwrap(handler.member_add_patch)(handler, id_=sample_room.id, body={"id": 1})
        assert status == 204

    async def test_member_del_patch(self, handler, mock_room_manager, sample_room):
        mock_room_manager.remove_member = AsyncMock(return_value=None)
        handler.member_delete = AsyncMock(return_value=(None, 204))
        result, status = await unwrap(handler.member_del_patch)(handler, id_=sample_room.id, member_id=1)
        assert status == 204

    def test_member_get_sync(self, handler, mock_room_manager, sample_room):
        mock_room_manager.room_from_member = MagicMock(return_value=sample_room)
        result, status = unwrap(handler.member_get)(handler, id_=28)
        assert status == 200


# ===========================================================================
# PortHandler tests
# ===========================================================================
class TestPortHandler:
    @fixture
    def mock_port_manager(self):
        from adh6.network.port_manager import PortManager

        return MagicMock(spec=PortManager)

    @fixture
    def mock_switch_network_manager(self):
        from adh6.network.interfaces import SwitchNetworkManager

        return MagicMock(spec=SwitchNetworkManager)

    @fixture
    def handler(self, mock_port_manager, mock_switch_network_manager):
        from adh6.network.http.port import PortHandler

        return PortHandler(
            port_manager=mock_port_manager,
            switch_network_manager=mock_switch_network_manager,
        )

    PORT_ID = 7

    def test_state_get(self, handler, mock_switch_network_manager):
        mock_switch_network_manager.get_port_status = MagicMock(return_value="up")
        result, status = unwrap(handler.state_get)(handler, id_=self.PORT_ID)
        assert status == 200

    def test_state_put(self, handler, mock_switch_network_manager):
        mock_switch_network_manager.update_port_status = MagicMock(return_value="up")
        result, status = unwrap(handler.state_put)(handler, id_=self.PORT_ID)
        assert status == 200

    async def test_vlan_get(self, handler, mock_switch_network_manager):
        mock_switch_network_manager.get_port_vlan = AsyncMock(return_value="41")
        result, status = await unwrap(handler.vlan_get)(handler, id_=self.PORT_ID)
        assert status == 200
        assert result == 41

    async def test_vlan_get_no_such_instance(self, handler, mock_switch_network_manager):
        mock_switch_network_manager.get_port_vlan = AsyncMock(
            return_value="No Such Instance currently exists at this OID"
        )
        result, status = await unwrap(handler.vlan_get)(handler, id_=self.PORT_ID)
        assert result == 1

    async def test_vlan_put(self, handler, mock_switch_network_manager):
        mock_switch_network_manager.get_port_vlan = AsyncMock(return_value="41")
        mock_switch_network_manager.update_port_vlan = AsyncMock(return_value=None)
        result, status = await unwrap(handler.vlan_put)(handler, id_=self.PORT_ID, body=41)
        assert status == 204

    def test_mab_get(self, handler, mock_switch_network_manager):
        mock_switch_network_manager.get_port_mab = MagicMock(return_value="true")
        result, status = unwrap(handler.mab_get)(handler, id_=self.PORT_ID)
        assert result is True

    def test_mab_put(self, handler, mock_switch_network_manager):
        mock_switch_network_manager.update_port_mab = MagicMock(return_value="true")
        result, status = unwrap(handler.mab_put)(handler, id_=self.PORT_ID)
        assert result is True

    def test_auth_get(self, handler, mock_switch_network_manager):
        mock_switch_network_manager.get_port_auth = MagicMock(return_value="auto")
        result, status = unwrap(handler.auth_get)(handler, id_=self.PORT_ID)
        assert result is True

    def test_auth_put(self, handler, mock_switch_network_manager):
        mock_switch_network_manager.update_port_auth = MagicMock(return_value="auto")
        result, status = unwrap(handler.auth_put)(handler, id_=self.PORT_ID)
        assert result is True

    def test_use_get(self, handler, mock_switch_network_manager):
        mock_switch_network_manager.get_port_use = MagicMock(return_value="access")
        result, status = unwrap(handler.use_get)(handler, id_=self.PORT_ID)
        assert result == "access"

    def test_alias_get(self, handler, mock_switch_network_manager):
        mock_switch_network_manager.get_port_alias = MagicMock(return_value="port-alias")
        result, status = unwrap(handler.alias_get)(handler, id_=self.PORT_ID)
        assert result == "port-alias"

    def test_speed_get(self, handler, mock_switch_network_manager):
        mock_switch_network_manager.get_port_speed = MagicMock(return_value="1Gbps")
        result, status = unwrap(handler.speed_get)(handler, id_=self.PORT_ID)
        assert result == "1Gbps"


# ===========================================================================
# CharterHandler tests
# ===========================================================================
class TestCharterHandler:
    @fixture
    def mock_charter_manager(self):
        from adh6.member.charter_manager import CharterManager

        return MagicMock(spec=CharterManager)

    @fixture
    def handler(self, mock_charter_manager):
        from adh6.member.http.charter import CharterHandler

        return CharterHandler(charter_manager=mock_charter_manager)

    async def test_member_search(self, handler, mock_charter_manager):
        mock_charter_manager.get_members = AsyncMock(return_value=([], 0))
        result, status, headers = await unwrap(handler.member_search)(handler, charter_id=1)
        assert status == 200
        assert "X-Total-Count" in headers

    async def test_member_get(self, handler, mock_charter_manager, sample_member):
        mock_charter_manager.get = AsyncMock(return_value=None)
        result, status = await unwrap(handler.member_get)(handler, charter_id=1, id_=sample_member.id)
        assert status == 200
        assert result == ""

    async def test_member_post(self, handler, mock_charter_manager, sample_member):
        mock_charter_manager.sign = AsyncMock(return_value=None)
        result, status = await unwrap(handler.member_post)(handler, charter_id=1, id_=sample_member.id)
        assert status == 201


# ===========================================================================
# MailinglistHandler tests
# ===========================================================================
class TestMailinglistHandler:
    @fixture
    def mock_mailinglist_manager(self):
        from adh6.member.mailinglist_manager import MailinglistManager

        return MagicMock(spec=MailinglistManager)

    @fixture
    def handler(self, mock_mailinglist_manager):
        from adh6.member.http.mailinglist import MailinglistHandler

        return MailinglistHandler(mailinglist_manager=mock_mailinglist_manager)

    async def test_member_get(self, handler, mock_mailinglist_manager, sample_member):
        mock_mailinglist_manager.get_member_mailinglist = AsyncMock(return_value=128)
        result, status = await unwrap(handler.member_get)(handler, id_=sample_member.id)
        assert status == 200
        assert result == 128

    async def test_member_put(self, handler, mock_mailinglist_manager, sample_member):
        mock_mailinglist_manager.update_member_mailinglist = AsyncMock(return_value=None)
        result, status = await unwrap(handler.member_put)(handler, id_=sample_member.id, body={"value": 64})
        assert status == 204

    async def test_search(self, handler, mock_mailinglist_manager):
        mock_mailinglist_manager.get_members = AsyncMock(return_value=[1, 2, 3])
        result, status = await unwrap(handler.search)(handler, value=128)
        assert status == 200


# ===========================================================================
# ProductHandler tests
# ===========================================================================
class TestProductHandler:
    @fixture
    def mock_product_manager(self):
        from adh6.treasury.product_manager import ProductManager

        return MagicMock(spec=ProductManager)

    @fixture
    def handler(self, mock_product_manager):
        from adh6.treasury.http.product import ProductHandler

        return ProductHandler(product_manager=mock_product_manager)

    @fixture
    def sample_product(self, faker):
        return MagicMock(to_dict=lambda: {"id": 1, "name": "Test Product", "sellingPrice": 100, "buyingPrice": 50})

    async def test_search(self, handler, mock_product_manager, sample_product):
        mock_product_manager.search = AsyncMock(return_value=([sample_product], 1))
        result, status, headers = await unwrap(handler.search)(handler)
        assert status == 200

    async def test_get(self, handler, mock_product_manager, sample_product):
        mock_product_manager.get_by_id = AsyncMock(return_value=sample_product)
        result, status = await unwrap(handler.get)(handler, id_=1)
        assert status == 200

    async def test_buy_post(self, handler, mock_product_manager):
        mock_product_manager.buy = AsyncMock(return_value=None)
        result, status = await unwrap(handler.buy_post)(handler, member_id=28, payment_method=1, products=[1, 2])
        assert status == 204


# ===========================================================================
# RoleHandler tests
# ===========================================================================
class TestRoleHandler:
    @fixture
    def mock_role_manager(self):
        from adh6.authentication.role_manager import RoleManager

        return MagicMock(spec=RoleManager)

    @fixture
    def handler(self, mock_role_manager):
        from adh6.authentication.http.role import RoleHandler

        return RoleHandler(role_manager=mock_role_manager)

    async def test_search(self, handler, mock_role_manager):
        mock_role_manager.search = AsyncMock(return_value=([], 0))
        result, status, headers = await unwrap(handler.search)(handler, auth="user", id_=None)
        assert status == 200

    async def test_post(self, handler, mock_role_manager):
        mock_role_manager.create = AsyncMock(return_value=None)
        body = {"auth": "user", "identifier": "testuser", "roles": ["user:read"]}
        result, status = await unwrap(handler.post)(handler, body=body)
        assert status == 201

    async def test_delete(self, handler, mock_role_manager):
        mock_role_manager.delete = AsyncMock(return_value=None)
        result, status = await unwrap(handler.delete)(handler, id_=1)
        assert status == 204


# ===========================================================================
# ApiKeyHandler tests
# ===========================================================================
class TestApiKeyHandler:
    @fixture
    def mock_api_key_manager(self):
        from adh6.authentication.api_keys_manager import ApiKeyManager

        return MagicMock(spec=ApiKeyManager)

    @fixture
    def handler(self, mock_api_key_manager):
        from adh6.authentication.http.api_key import ApiKeyHandler

        return ApiKeyHandler(api_key_manager=mock_api_key_manager)

    async def test_search(self, handler, mock_api_key_manager):
        mock_api_key_manager.search = AsyncMock(return_value=([], 0))
        result, status, headers = await unwrap(handler.search)(handler, limit=10, offset=0, login=None)
        assert status == 200

    async def test_post(self, handler, mock_api_key_manager):
        mock_api_key_manager.create = AsyncMock(return_value="new-api-key-value")
        result, status = await unwrap(handler.post)(handler, body={"login": "testuser", "roles": ["user:read"]})
        assert status == 200

    async def test_delete(self, handler, mock_api_key_manager):
        mock_api_key_manager.delete = AsyncMock(return_value=None)
        result, status = await unwrap(handler.delete)(handler, id_=1)
        assert status == 204


# ===========================================================================
# DefaultHandler tests
# ===========================================================================
class TestDefaultHandler:
    @fixture
    def mock_manager(self):
        from adh6.default.crud_manager import CRUDManager

        m = MagicMock(spec=CRUDManager)
        return m

    @fixture
    def sample_room(self):
        from adh6.entity import Room

        return Room(id=1, roomNumber=100, vlan=41, description="Test room")

    @fixture
    def handler(self, mock_manager):
        from adh6.default.http_handler import DefaultHandler
        from adh6.entity import AbstractRoom, Room

        return DefaultHandler(
            entity_class=Room,
            abstract_entity_class=AbstractRoom,
            main_manager=mock_manager,
        )

    async def test_search(self, handler, mock_manager, sample_room):
        mock_manager.search = AsyncMock(return_value=([sample_room], 1))
        result, status, headers = await unwrap(handler.search)(handler, limit=10, offset=0)
        assert status == 200

    async def test_search_with_only_filter(self, handler, mock_manager, sample_room):
        mock_manager.search = AsyncMock(return_value=([sample_room], 1))
        result, status, headers = await unwrap(handler.search)(handler, limit=10, offset=0, only=["roomNumber"])
        assert status == 200

    async def test_get(self, handler, mock_manager, sample_room):
        mock_manager.get_by_id = AsyncMock(return_value=sample_room)
        result, status = await unwrap(handler.get)(handler, id_=1)
        assert status == 200

    async def test_get_with_only(self, handler, mock_manager, sample_room):
        mock_manager.get_by_id = AsyncMock(return_value=sample_room)
        result, status = await unwrap(handler.get)(handler, id_=1, only=["roomNumber"])
        assert status == 200

    async def test_delete(self, handler, mock_manager):
        mock_manager.delete = AsyncMock(return_value=None)
        result, status = await unwrap(handler.delete)(handler, id_=1)
        assert result is None
        assert status == 204

    async def test_patch(self, handler, mock_manager, sample_room):
        mock_manager.partially_update = AsyncMock(return_value=(sample_room, False))
        body = {"roomNumber": 100, "vlan": 41, "description": "Test room"}
        result, status = await unwrap(handler.patch)(handler, body=body, id_=1)
        assert status == 204

    async def test_post(self, handler, mock_manager, sample_room):
        mock_manager.update_or_create = AsyncMock(return_value=(sample_room, True))
        body = {"roomNumber": 100, "vlan": 41, "description": "Test room"}
        result, status = await unwrap(handler.post)(handler, body=body)
        assert status == 201

    async def test_put(self, handler, mock_manager, sample_room):
        mock_manager.update_or_create = AsyncMock(return_value=(sample_room, False))
        body = {"roomNumber": 100, "vlan": 41, "description": "Test room"}
        result, status = await unwrap(handler.put)(handler, body=body, id_=1)
        assert status == 204
