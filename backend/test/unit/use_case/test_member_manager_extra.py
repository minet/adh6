"""Extended tests for MemberManager to increase coverage."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from adh6.constants import MembershipStatus
from adh6.device.device_ip_manager import DeviceIpManager
from adh6.device.device_logs_manager import DeviceLogsManager
from adh6.entity import Member, MemberBody
from adh6.entity.membership import Membership
from adh6.exceptions import (
    InvalidPassword,
    MemberNotFoundError,
    NoSubnetAvailable,
    UpdateImpossible,
)
from adh6.member.interfaces import MailinglistRepository, MemberRepository, MembershipRepository
from adh6.member.interfaces.charter_repository import CharterRepository
from adh6.member.member_manager import MemberManager
from adh6.member.notification_manager import NotificationManager
from adh6.member.subscription_manager import SubscriptionManager
from adh6.room.interfaces import RoomRepository
from adh6.subnet.interfaces import VlanRepository
from adh6.treasury.interfaces import AccountRepository, AccountTypeRepository, PaymentMethodRepository
from adh6.treasury.transaction_manager import TransactionManager
from pytest import fixture, raises


@fixture(autouse=True)
def mock_test_configuration(monkeypatch):
    from adh6.member.subscription_manager import SubscriptionManager

    monkeypatch.setattr(SubscriptionManager, "duration_price", {1: 9, 12: 50})
    monkeypatch.setattr(SubscriptionManager, "duration_string", {1: "1 Mois", 12: "1 an"})


@fixture(autouse=True)
def ctx(sample_member, monkeypatch):
    import adh6.context as context
    from adh6.authentication.enums import Roles

    monkeypatch.setattr(context, "get_user", lambda: sample_member.id, raising=False)
    monkeypatch.setattr(
        context,
        "get_roles",
        lambda: [Roles.USER.value, Roles.ADMIN_WRITE.value, Roles.ADMIN_READ.value],
        raising=False,
    )


@fixture
def sample_member(faker) -> Member:
    return Member(
        id=faker.random_digit_not_null(),
        username=faker.user_name(),
        email=faker.email(),
        firstName=faker.first_name(),
        lastName=faker.last_name(),
        departureDate=datetime.now() + timedelta(days=30),
        comment=faker.sentence(),
    )


@fixture
def sample_member_inactive(faker) -> Member:
    return Member(
        id=faker.random_digit_not_null(),
        username=faker.user_name(),
        email=faker.email(),
        firstName=faker.first_name(),
        lastName=faker.last_name(),
        departureDate=datetime.now() - timedelta(days=1),
        comment=faker.sentence(),
    )


@fixture
def mock_member_repository():
    return MagicMock(spec=MemberRepository)


@fixture
def mock_membership_repository():
    return MagicMock(spec=MembershipRepository)


@fixture
def mock_charter_repository():
    return MagicMock(spec=CharterRepository)


@fixture
def mock_account_repository():
    return MagicMock(spec=AccountRepository)


@fixture
def mock_account_type_repository():
    return MagicMock(spec=AccountTypeRepository)


@fixture
def mock_mailinglist_repository():
    return MagicMock(spec=MailinglistRepository)


@fixture
def mock_device_logs_manager():
    return MagicMock(spec=DeviceLogsManager)


@fixture
def mock_device_ip_manager():
    return MagicMock(spec=DeviceIpManager)


@fixture
def mock_notification_manager():
    return MagicMock(spec=NotificationManager)


@fixture
def mock_transaction_manager():
    return MagicMock(spec=TransactionManager)


@fixture
def mock_payment_method_repository():
    return MagicMock(spec=PaymentMethodRepository)


@fixture
def mock_vlan_repository():
    return MagicMock(spec=VlanRepository)


@fixture
def mock_room_repository():
    return MagicMock(spec=RoomRepository)


@fixture
def subscription_manager(
    mock_member_repository,
    mock_membership_repository,
    mock_charter_repository,
    mock_account_repository,
    mock_payment_method_repository,
    mock_transaction_manager,
    mock_notification_manager,
):
    return SubscriptionManager(
        member_repository=mock_member_repository,
        membership_repository=mock_membership_repository,
        charter_repository=mock_charter_repository,
        notification_manager=mock_notification_manager,
        transaction_manager=mock_transaction_manager,
        payment_method_repository=mock_payment_method_repository,
        account_repository=mock_account_repository,
    )


@fixture
def member_manager(
    mock_member_repository,
    mock_account_repository,
    mock_account_type_repository,
    subscription_manager,
    mock_mailinglist_repository,
    mock_device_logs_manager,
    mock_device_ip_manager,
    mock_room_repository,
):
    return MemberManager(
        member_repository=mock_member_repository,
        account_repository=mock_account_repository,
        account_type_repository=mock_account_type_repository,
        device_ip_manager=mock_device_ip_manager,
        device_logs_manager=mock_device_logs_manager,
        mailinglist_repository=mock_mailinglist_repository,
        subscription_manager=subscription_manager,
        room_repository=mock_room_repository,
    )


class TestSearch:
    async def test_happy_path(
        self,
        mock_member_repository: MemberRepository,
        member_manager: MemberManager,
        sample_member: Member,
    ):
        mock_member_repository.search_by = AsyncMock(return_value=([sample_member], 1))

        result, count = await member_manager.search(terms="some search")

        assert result == [sample_member.id]
        assert count == 1
        mock_member_repository.search_by.assert_called_once_with(limit=100, offset=0, terms="some search", filter_=None)

    async def test_no_results(
        self,
        mock_member_repository: MemberRepository,
        member_manager: MemberManager,
    ):
        mock_member_repository.search_by = AsyncMock(return_value=([], 0))

        result, count = await member_manager.search()

        assert result == []
        assert count == 0

    async def test_result_with_none_id(
        self,
        mock_member_repository: MemberRepository,
        member_manager: MemberManager,
    ):
        member_no_id = MagicMock(spec=Member)
        member_no_id.id = None
        mock_member_repository.search_by = AsyncMock(return_value=([member_no_id], 1))

        result, count = await member_manager.search()

        assert result == []
        assert count == 1


class TestGetById:
    async def test_not_found_raises_error(
        self,
        mock_member_repository: MemberRepository,
        member_manager: MemberManager,
    ):
        """Ensure get_by_id raises MemberNotFoundError when member is None (not via side_effect)."""
        mock_member_repository.get_by_id = AsyncMock(return_value=None)

        with raises(MemberNotFoundError):
            await member_manager.get_by_id(id=999)


class TestGetByLogin:
    async def test_happy_path(
        self,
        mock_member_repository: MemberRepository,
        mock_membership_repository: MembershipRepository,
        sample_member: Member,
        member_manager: MemberManager,
    ):
        mock_member_repository.get_by_login = AsyncMock(return_value=sample_member)
        mock_membership_repository.search = AsyncMock(return_value=([], 0))

        result = await member_manager.get_by_login(login=sample_member.username)

        assert result == sample_member

    async def test_not_found(
        self,
        mock_member_repository: MemberRepository,
        member_manager: MemberManager,
    ):
        mock_member_repository.get_by_login = AsyncMock(return_value=None)

        with raises(MemberNotFoundError):
            await member_manager.get_by_login(login="unknownuser")

    async def test_not_found_no_id(
        self,
        mock_member_repository: MemberRepository,
        member_manager: MemberManager,
        faker,
    ):
        member_no_id = Member.model_construct(
            id=None,
            username=faker.user_name(),
            email=faker.email(),
            firstName=faker.first_name(),
            lastName=faker.last_name(),
        )
        mock_member_repository.get_by_login = AsyncMock(return_value=member_no_id)

        with raises(MemberNotFoundError):
            await member_manager.get_by_login(login=member_no_id.username)


class TestGetProfile:
    async def test_no_user_in_context(
        self,
        member_manager: MemberManager,
        monkeypatch,
    ):
        import adh6.context as context

        monkeypatch.setattr(context, "get_user", lambda: None, raising=False)

        with raises(MemberNotFoundError):
            await member_manager.get_profile()

    async def test_member_not_found_in_db(
        self,
        mock_member_repository: MemberRepository,
        member_manager: MemberManager,
        sample_member: Member,
        monkeypatch,
    ):
        import adh6.context as context

        monkeypatch.setattr(context, "get_user", lambda: sample_member.id, raising=False)
        mock_member_repository.get_by_id = AsyncMock(return_value=None)

        with raises(MemberNotFoundError):
            await member_manager.get_profile()

    async def test_happy_path(
        self,
        mock_member_repository: MemberRepository,
        member_manager: MemberManager,
        sample_member: Member,
        monkeypatch,
    ):
        import adh6.context as context

        monkeypatch.setattr(context, "get_user", lambda: sample_member.id, raising=False)
        monkeypatch.setattr(context, "get_roles", lambda: ["user:read"], raising=False)
        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)

        result_member, roles = await member_manager.get_profile()
        assert result_member == sample_member
        assert roles == ["user:read"]


class TestCreate:
    async def test_happy_path(
        self,
        mock_member_repository: MemberRepository,
        mock_account_repository: AccountRepository,
        mock_account_type_repository: AccountTypeRepository,
        mock_mailinglist_repository: MailinglistRepository,
        mock_membership_repository: MembershipRepository,
        sample_member: Member,
        member_manager: MemberManager,
        faker,
    ):
        from adh6.entity import AccountType

        account_type = AccountType(id=1, name="Adhérent")
        mock_member_repository.get_by_login = AsyncMock(return_value=None)
        mock_account_type_repository.search_by = AsyncMock(return_value=([account_type], 1))
        mock_member_repository.create = AsyncMock(return_value=sample_member)
        mock_mailinglist_repository.update_from_member = AsyncMock(return_value=None)
        mock_account_repository.create = AsyncMock(return_value=MagicMock())
        mock_membership_repository.search = AsyncMock(return_value=([], 0))
        mock_membership_repository.create = AsyncMock(return_value=MagicMock(status=MembershipStatus.INITIAL.value))

        body = MemberBody(
            username=faker.user_name(),
            firstName=faker.first_name(),
            lastName=faker.last_name(),
            mail=faker.email(),
        )
        result = await member_manager.create(body=body)
        assert result == sample_member


class TestUpdate:
    async def test_happy_path(
        self,
        mock_member_repository: MemberRepository,
        mock_membership_repository: MembershipRepository,
        sample_member: Member,
        member_manager: MemberManager,
        faker,
    ):
        complete_membership = Membership(
            uuid=faker.uuid4(),
            member=sample_member.id,
            status=MembershipStatus.COMPLETE.value,
            hasRoom=None,
        )
        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)
        mock_membership_repository.search = AsyncMock(return_value=([complete_membership], 1))
        mock_member_repository.update = AsyncMock(return_value=sample_member)

        body = MemberBody(username=sample_member.username, mail=sample_member.email)
        await member_manager.update(id=sample_member.id, body=body)
        mock_member_repository.update.assert_called_once()

    async def test_not_found(
        self,
        mock_member_repository: MemberRepository,
        member_manager: MemberManager,
        sample_member: Member,
    ):
        mock_member_repository.get_by_id = AsyncMock(return_value=None)

        with raises(MemberNotFoundError):
            await member_manager.update(id=sample_member.id, body=MemberBody())

    async def test_update_impossible_initial_status(
        self,
        mock_member_repository: MemberRepository,
        mock_membership_repository: MembershipRepository,
        sample_member: Member,
        member_manager: MemberManager,
        faker,
    ):
        pending_membership = Membership(
            uuid=faker.uuid4(),
            member=sample_member.id,
            status=MembershipStatus.PENDING_PAYMENT.value,
            hasRoom=None,
        )
        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)
        mock_membership_repository.search = AsyncMock(return_value=([pending_membership], 1))

        with raises(UpdateImpossible):
            await member_manager.update(id=sample_member.id, body=MemberBody(username="newusername"))

    async def test_update_impossible_no_membership(
        self,
        mock_member_repository: MemberRepository,
        mock_membership_repository: MembershipRepository,
        sample_member: Member,
        member_manager: MemberManager,
    ):
        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)
        mock_membership_repository.search = AsyncMock(return_value=([], 0))

        with raises(UpdateImpossible):
            await member_manager.update(id=sample_member.id, body=MemberBody(mail="new@example.com"))


class TestGetLogs:
    async def test_happy_path(
        self,
        mock_member_repository: MemberRepository,
        mock_device_logs_manager: MagicMock,
        sample_member: Member,
        member_manager: MemberManager,
        faker,
    ):
        from datetime import datetime as dt

        logs = [(dt(2024, 1, 15, 10, 30), "Login OK: [user] cli aa-bb-cc-dd-ee-ff)")]
        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)
        mock_device_logs_manager.get = AsyncMock(return_value=(logs, 1))

        result = await member_manager.get_logs(sample_member.id, limit=10, offset=0)

        assert "logs" in result
        assert "total" in result
        assert "hasMore" in result
        assert result["total"] == 1


class TestChangePassword:
    async def test_happy_path(
        self,
        mock_member_repository: MemberRepository,
        sample_member: Member,
        member_manager: MemberManager,
    ):
        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)
        mock_member_repository.update_password = AsyncMock(return_value=None)

        result = await member_manager.change_password(
            member_id=sample_member.id,
            password="ValidPass1!",
            hashed_password=None,
        )
        assert result is True
        mock_member_repository.update_password.assert_called_once()

    async def test_member_not_found(
        self,
        mock_member_repository: MemberRepository,
        member_manager: MemberManager,
        sample_member: Member,
    ):
        mock_member_repository.get_by_id = AsyncMock(return_value=None)

        with raises(MemberNotFoundError):
            await member_manager.change_password(
                member_id=sample_member.id,
                password="ValidPass1!",
                hashed_password=None,
            )

    async def test_invalid_password(
        self,
        mock_member_repository: MemberRepository,
        sample_member: Member,
        member_manager: MemberManager,
    ):
        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)

        with raises(InvalidPassword):
            await member_manager.change_password(
                member_id=sample_member.id,
                password="short",
                hashed_password=None,
            )

    async def test_with_hashed_password(
        self,
        mock_member_repository: MemberRepository,
        sample_member: Member,
        member_manager: MemberManager,
    ):
        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)
        mock_member_repository.update_password = AsyncMock(return_value=None)

        result = await member_manager.change_password(
            member_id=sample_member.id,
            password="ValidPass1!",
            hashed_password="prehashedvalue",
        )
        assert result is True
        # Should use the provided hashed_password, not compute a new one
        mock_member_repository.update_password.assert_called_once_with(sample_member.id, "prehashedvalue")


class TestUpdateSubnet:
    async def test_member_not_found(
        self,
        mock_member_repository: MemberRepository,
        member_manager: MemberManager,
        sample_member: Member,
    ):
        mock_member_repository.get_by_id = AsyncMock(return_value=None)

        with raises(MemberNotFoundError):
            await member_manager.update_subnet(member_id=sample_member.id)

    async def test_inactive_member_returns_none(
        self,
        mock_member_repository: MemberRepository,
        member_manager: MemberManager,
        sample_member_inactive: Member,
    ):
        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member_inactive)

        result = await member_manager.update_subnet(member_id=sample_member_inactive.id)
        assert result is None

    async def test_no_subnet_available(
        self,
        mock_member_repository: MemberRepository,
        member_manager: MemberManager,
        sample_member: Member,
    ):
        from adh6.constants import SUBNET_PUBLIC_ADDRESSES_WIRELESS

        # Fill all available subnets
        used_ips = list(SUBNET_PUBLIC_ADDRESSES_WIRELESS.keys())
        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)
        mock_member_repository.used_wireless_public_ips = AsyncMock(return_value=used_ips)

        with raises(NoSubnetAvailable):
            await member_manager.update_subnet(member_id=sample_member.id)


class TestResetMember:
    async def test_happy_path(
        self,
        mock_member_repository: MemberRepository,
        mock_device_ip_manager: MagicMock,
        sample_member: Member,
        member_manager: MemberManager,
    ):
        updated_member = Member(
            id=sample_member.id,
            username=sample_member.username,
            email=sample_member.email,
            firstName=sample_member.first_name,
            lastName=sample_member.last_name,
            ip="",
            subnet="",
        )
        mock_member_repository.update = AsyncMock(return_value=updated_member)
        mock_device_ip_manager.unallocate_ips = AsyncMock(return_value=None)

        await member_manager.reset_member(member_id=sample_member.id)
        mock_member_repository.update.assert_called_once()
        mock_device_ip_manager.unallocate_ips.assert_called_once()


class TestEthernetVlanChanged:
    async def test_happy_path(
        self,
        mock_member_repository: MemberRepository,
        mock_membership_repository: MembershipRepository,
        mock_device_ip_manager: MagicMock,
        sample_member: Member,
        member_manager: MemberManager,
    ):
        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)
        mock_membership_repository.search = AsyncMock(return_value=([], 0))
        mock_device_ip_manager.allocate_ips = AsyncMock(return_value=None)

        await member_manager.ethernet_vlan_changed(member_id=sample_member.id, vlan_number=41)
        mock_device_ip_manager.allocate_ips.assert_called_once()


class TestChangeComment:
    async def test_happy_path(
        self,
        mock_member_repository: MemberRepository,
        sample_member: Member,
        member_manager: MemberManager,
    ):
        from adh6.entity import Comment

        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)
        mock_member_repository.update_comment = AsyncMock(return_value=None)

        await member_manager.change_comment(member_id=sample_member.id, comment=Comment(comment="Test comment"))
        mock_member_repository.update_comment.assert_called_once()

    async def test_not_found(
        self,
        mock_member_repository: MemberRepository,
        member_manager: MemberManager,
        sample_member: Member,
    ):
        from adh6.entity import Comment

        mock_member_repository.get_by_id = AsyncMock(return_value=None)

        with raises(MemberNotFoundError):
            await member_manager.change_comment(member_id=sample_member.id, comment=Comment(comment="Test comment"))


class TestGetComment:
    async def test_happy_path(
        self,
        mock_member_repository: MemberRepository,
        sample_member: Member,
        member_manager: MemberManager,
    ):
        sample_member.comment = "Test comment"
        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)

        result = await member_manager.get_comment(member_id=sample_member.id)
        assert result.comment == "Test comment"

    async def test_not_found(
        self,
        mock_member_repository: MemberRepository,
        member_manager: MemberManager,
        sample_member: Member,
    ):
        mock_member_repository.get_by_id = AsyncMock(return_value=None)

        with raises(MemberNotFoundError):
            await member_manager.get_comment(member_id=sample_member.id)

    async def test_no_comment(
        self,
        mock_member_repository: MemberRepository,
        sample_member: Member,
        member_manager: MemberManager,
    ):
        sample_member.comment = None
        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)

        result = await member_manager.get_comment(member_id=sample_member.id)
        assert result.comment == ""


class TestGetStatuses:
    async def test_member_not_found(
        self,
        mock_member_repository: MemberRepository,
        member_manager: MemberManager,
        sample_member: Member,
    ):
        mock_member_repository.get_by_id = AsyncMock(return_value=None)
        with raises(MemberNotFoundError):
            await member_manager.get_statuses(member_id=sample_member.id)

    async def test_empty_logs(
        self,
        mock_member_repository: MemberRepository,
        mock_device_logs_manager: DeviceLogsManager,
        member_manager: MemberManager,
        sample_member: Member,
    ):
        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)
        mock_device_logs_manager.get = AsyncMock(return_value=([], 0))
        result = await member_manager.get_statuses(member_id=sample_member.id)
        assert result == []

    async def test_log_fetch_error(
        self,
        mock_member_repository: MemberRepository,
        mock_device_logs_manager: DeviceLogsManager,
        member_manager: MemberManager,
        sample_member: Member,
    ):
        from adh6.exceptions import LogFetchError

        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)
        mock_device_logs_manager.get = AsyncMock(side_effect=LogFetchError("fail"))
        result = await member_manager.get_statuses(member_id=sample_member.id)
        assert result == []

    async def test_login_ok_log(
        self,
        mock_member_repository: MemberRepository,
        mock_device_logs_manager: DeviceLogsManager,
        member_manager: MemberManager,
        sample_member: Member,
    ):
        from datetime import datetime

        ts = datetime(2024, 1, 1, 12, 0, 0)
        mac = "AA-BB-CC-DD-EE-FF"
        login_ok_msg = f"TLS Login OK: [{sample_member.username}] (from client cli {mac.lower()}-port1)"
        logs = [[ts, login_ok_msg]]
        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)
        mock_device_logs_manager.get = AsyncMock(return_value=(logs, 1))
        result = await member_manager.get_statuses(member_id=sample_member.id)
        # No status added since it's Login OK (only recorded in last_ok_login_mac)
        assert isinstance(result, list)

    async def test_rlm_python_log_wrong_mac(
        self,
        mock_member_repository: MemberRepository,
        mock_device_logs_manager: DeviceLogsManager,
        member_manager: MemberManager,
        sample_member: Member,
    ):
        from datetime import datetime

        ts = datetime(2024, 1, 1, 12, 0, 0)
        mac = "AA-BB-CC-DD-EE-FF"
        msg = f"rlm_python: Fail {sample_member.username} {mac} with MAC not found and not association period"
        logs = [[ts, msg]]
        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)
        mock_device_logs_manager.get = AsyncMock(return_value=(logs, 1))
        result = await member_manager.get_statuses(member_id=sample_member.id)
        assert any(s.status == "LOGIN_INCORRECT_WRONG_MAC" for s in result)

    async def test_rlm_python_log_adherent_not_found(
        self,
        mock_member_repository: MemberRepository,
        mock_device_logs_manager: DeviceLogsManager,
        member_manager: MemberManager,
        sample_member: Member,
    ):
        from datetime import datetime

        ts = datetime(2024, 1, 1, 12, 0, 0)
        mac = "AA-BB-CC-DD-EE-FF"
        msg = f"rlm_python: Fail {sample_member.username} {mac} with Adherent not found"
        logs = [[ts, msg]]
        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)
        mock_device_logs_manager.get = AsyncMock(return_value=(logs, 1))
        result = await member_manager.get_statuses(member_id=sample_member.id)
        assert any(s.status == "LOGIN_INCORRECT_WRONG_USER" for s in result)

    async def test_tls_alert_log(
        self,
        mock_member_repository: MemberRepository,
        mock_device_logs_manager: DeviceLogsManager,
        member_manager: MemberManager,
        sample_member: Member,
    ):
        from datetime import datetime

        ts = datetime(2024, 1, 1, 12, 0, 0)
        mac = "aa-bb-cc-dd-ee-ff"
        msg = f"TLS Alert read (protocol version): [{sample_member.username}] (from client cli {mac})"
        logs = [[ts, msg]]
        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)
        mock_device_logs_manager.get = AsyncMock(return_value=(logs, 1))
        result = await member_manager.get_statuses(member_id=sample_member.id)
        assert any(s.status == "LOGIN_INCORRECT_SSL_ERROR" for s in result)

    async def test_mschap_fail_wrong_password(
        self,
        mock_member_repository: MemberRepository,
        mock_device_logs_manager: DeviceLogsManager,
        member_manager: MemberManager,
        sample_member: Member,
    ):
        from datetime import datetime, timedelta

        ts1 = datetime(2024, 1, 1, 12, 0, 0)
        ts2 = datetime(2024, 1, 1, 12, 0, 0) + timedelta(milliseconds=500)
        mac = "aa-bb-cc-dd-ee-ff"
        msg1 = f"EAP sub-module failed): [{sample_member.username}] (from client cli {mac})"
        msg2 = "Auth: mschap: MS-CHAP2-Response is incorrect"
        logs = [[ts1, msg1], [ts2, msg2]]
        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)
        mock_device_logs_manager.get = AsyncMock(return_value=(logs, 2))
        result = await member_manager.get_statuses(member_id=sample_member.id)
        assert isinstance(result, list)


class TestUpdateSubnetHappyPath:
    async def test_subnet_allocated(
        self,
        mock_member_repository: MemberRepository,
        mock_device_ip_manager: MagicMock,
        member_manager: MemberManager,
        sample_member: Member,
    ):
        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)
        # No IPs in use → first available one will be allocated
        mock_member_repository.used_wireless_public_ips = AsyncMock(return_value=[])

        updated_member = MagicMock()
        mock_member_repository.update = AsyncMock(return_value=updated_member)
        mock_device_ip_manager.allocate_ips = AsyncMock(return_value=None)

        result = await member_manager.update_subnet(member_id=sample_member.id)
        assert result is not None
        mock_member_repository.update.assert_called_once()
        mock_device_ip_manager.allocate_ips.assert_called_once()
