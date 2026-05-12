from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.constants import MembershipDuration, MembershipStatus
from adh6.device.device_ip_manager import DeviceIpManager
from adh6.device.device_logs_manager import DeviceLogsManager
from adh6.device.interfaces import IpAllocator, LogsRepository, NetboxRepository
from adh6.device.interfaces.device_repository import DeviceRepository
from adh6.entity import AbstractMember, Member, Membership
from adh6.entity.member_body import MemberBody
from adh6.exceptions import (
    LogFetchError,
    MemberAlreadyExist,
    MemberNotFoundError,
)
from adh6.member.interfaces import (
    MailinglistRepository,
    MemberRepository,
    MembershipRepository,
)
from adh6.member.interfaces.charter_repository import CharterRepository
from adh6.member.member_manager import MemberManager
from adh6.member.notification_manager import NotificationManager
from adh6.member.subscription_manager import SubscriptionManager
from adh6.room.interfaces import RoomRepository
from adh6.subnet.interfaces import VlanRepository
from adh6.treasury.interfaces import PaymentMethodRepository
from adh6.treasury.transaction_manager import TransactionManager
from pytest import fixture, raises

INVALID_MUTATION_REQ_ARGS = [
    ("empty_email", {"email": ""}),
    ("empty_first_name", {"first_name": ""}),
    ("empty_last_name", {"last_name": ""}),
    ("empty_username", {"username": ""}),
    ("empty_room_number", {"room_number": ""}),
    ("invalid_email", {"email": "not a valid email"}),
    ("invalid_username", {"username": "this username is way too long"}),
    ("invalid_association_mode", {"association_mode": "this is not a date"}),
    ("invalid_departure_date", {"departure_date": "this is not a date"}),
]

FAKE_LOGS_OBJ = [1, "blah blah blah logging logs"]
FAKE_LOGS = "1  "


class TestProfile:
    async def test_happy_path(
        self,
        mock_member_repository: MemberRepository,
        sample_member: Member,
        member_manager: MemberManager,
    ):
        mock_member_repository.get_by_id = AsyncMock(return_value=(sample_member))
        m, _ = await member_manager.get_profile()
        assert sample_member == m
        mock_member_repository.get_by_id.assert_called_once()

    async def test_member_not_found(self, mock_member_repository: MemberRepository, member_manager: MemberManager):
        # Given...
        mock_member_repository.get_by_id = AsyncMock(return_value=(None), side_effect=MemberNotFoundError(""))

        # When...
        with pytest.raises(MemberNotFoundError):
            await member_manager.get_profile()

        # Expect...
        mock_member_repository.get_by_id.assert_called_once()


class TestGetByID:
    async def test_happy_path(
        self,
        mock_member_repository: MemberRepository,
        mock_membership_repository: MembershipRepository,
        sample_member: Member,
        member_manager: MemberManager,
    ):
        # Given...
        mock_member_repository.get_by_id = AsyncMock(return_value=(sample_member))
        mock_membership_repository.search = AsyncMock(return_value=([], 0))

        # When...
        result = await member_manager.get_by_id(id=sample_member.id)

        # Expect...
        assert sample_member == result
        mock_member_repository.get_by_id.assert_called_once_with(sample_member.id)

    async def test_not_found(
        self,
        sample_member,
        mock_member_repository: MemberRepository,
        member_manager: MemberManager,
    ):
        # Given...
        mock_member_repository.get_by_id = AsyncMock(return_value=(None), side_effect=MemberNotFoundError(""))

        # When...
        with raises(MemberNotFoundError):
            await member_manager.get_by_id(id=sample_member.id)

        # Expect...
        mock_member_repository.get_by_id.assert_called_once_with(sample_member.id)


class TestSearch:
    async def test_happy_path(
        self,
        mock_member_repository: MemberRepository,
        sample_member: Member,
        member_manager: MemberManager,
    ):
        # Given...
        mock_member_repository.search_by = AsyncMock(return_value=([sample_member], 1))

        # When...
        test_terms = "blah blah blah"
        test_offset = 42
        test_limit = 99
        result, _ = await member_manager.search(limit=test_limit, offset=test_offset, terms=test_terms)

        # Expect...
        assert [sample_member.id] == result

        # Make sure that all the parameters are passed to the DB.
        mock_member_repository.search_by.assert_called_once_with(
            limit=test_limit, offset=test_offset, terms=test_terms, filter_=None
        )


class TestNewMember:
    async def test_member_already_exist(
        self,
        mock_member_repository: MemberRepository,
        sample_member: AbstractMember,
        member_manager: MemberManager,
    ):
        # Given...
        mock_member_repository.get_by_login = AsyncMock(return_value=(sample_member))

        # When...
        with pytest.raises(MemberAlreadyExist):
            await member_manager.create(body=MemberBody(username=sample_member.username))

        # Expect...
        mock_member_repository.get_by_login.assert_called_once_with(sample_member.username)


class TestCreateOrUpdate:
    async def test_create_happy_path(
        self,
        mock_member_repository: MagicMock,
        sample_mutation_request: AbstractMember,
        member_manager: MemberManager,
    ):
        # Given that there is not user in the DB (user will be created).
        mock_member_repository.search_by = AsyncMock(return_value=([], 0))

        # When...
        await member_manager.update_or_create(sample_mutation_request)

        # Expect...
        mock_member_repository.create.assert_called_once_with(sample_mutation_request)

    async def test_update_happy_path(
        self,
        mock_member_repository: MagicMock,
        sample_mutation_request: AbstractMember,
        sample_member: Member,
        member_manager: MemberManager,
    ):
        # Given that there is a user in the DB (user will be updated).
        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)

        # Given a request that updates some fields.
        req = sample_mutation_request
        req.comment = "Updated comment."
        req.first_name = "George"
        req.last_name = "Dupuis"

        # When...
        await member_manager.update_or_create(req, id=sample_member.id)

        # Expect...
        mock_member_repository.update.assert_called_once_with(req, override=True)
        mock_member_repository.create.assert_not_called()  # Do not create any member!


class TestUpdatePartially:
    async def test_happy_path(
        self,
        mock_member_repository: MagicMock,
        sample_member,
        member_manager: MemberManager,
    ):
        updated_comment = "Updated comment."
        req = AbstractMember(comment=updated_comment)

        # When...
        mock_member_repository.search_by = AsyncMock(return_value=([sample_member], 1))
        await member_manager.partially_update(req, id=sample_member.id)

        # Expect...
        mock_member_repository.update.assert_called_once_with(req, override=False)

    async def test_not_found(
        self,
        mock_member_repository: MagicMock,
        sample_member,
        member_manager: MemberManager,
    ):
        mock_member_repository.search_by = AsyncMock(return_value=([], 0))
        mock_member_repository.update = AsyncMock(side_effect=MemberNotFoundError)

        # When...
        with raises(MemberNotFoundError):
            await member_manager.partially_update(AbstractMember(id=sample_member.id), id=sample_member.id)


class TestDelete:
    async def test_delete_calls_reset_member(self, member_manager: MemberManager, mock_member_repository):
        member_id = 42
        mock_member_repository.get_by_id = AsyncMock(
            return_value=Member(
                id=member_id,
                username="u",
                firstName="f",
                lastName="l",
                email="e@e.com",
                subnet="10.0.0.0/24",
            )
        )
        mock_member_repository.delete = AsyncMock()
        member_manager.reset_member = AsyncMock()

        await member_manager.delete(member_id)

        member_manager.reset_member.assert_called_once_with(member_id)
        mock_member_repository.delete.assert_called_once_with(member_id)

    async def test_happy_path(
        self,
        mock_member_repository: MagicMock,
        sample_member,
        member_manager: MemberManager,
    ):
        # When...
        mock_member_repository.search_by = AsyncMock(return_value=([sample_member], 1))
        await member_manager.delete(id=sample_member.id)

        # Expect...
        mock_member_repository.delete.assert_called_once_with(sample_member.id)

    async def test_not_found(
        self,
        mock_member_repository: MagicMock,
        sample_member,
        member_manager: MemberManager,
    ):
        # Given...
        mock_member_repository.search_by = AsyncMock(return_value=([], 0))
        mock_member_repository.delete = AsyncMock(side_effect=MemberNotFoundError)

        # When...
        with raises(MemberNotFoundError):
            await member_manager.delete(id=sample_member.id)


class TestGetLogs:
    """
    async def test_happy_path(self,
                        mock_membership_repository: MembershipRepository,
                        mock_logs_repository: MagicMock,
                        mock_member_repository: MagicMock,
                        mock_device_repository: MagicMock,
                        sample_member: Member,
                        member_manager: MemberManager):
        # Given...
        mock_member_repository.search_by = AsyncMock(return_value=([sample_member], 1))
        mock_membership_repository.search = AsyncMock(return_value=([], 0))
        mock_logs_repository.get_logs = AsyncMock(return_value=([FAKE_LOGS]))

        # When...
        result = member_manager.get_logs(sample_member.id)

        # Expect...
        assert [FAKE_LOGS] == result
        devices = mock_device_repository.search_by(username=sample_member.username)
        mock_logs_repository.get_logs.assert_called_once_with(devices=devices.__getitem__(),
                                                              username=sample_member.username, dhcp=False)
    """

    async def test_fetch_failed(
        self,
        mock_membership_repository: MembershipRepository,
        mock_device_logs_manager: MagicMock,
        mock_member_repository: MagicMock,
        sample_member: Member,
        member_manager: MemberManager,
    ):
        # Given...
        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)
        mock_device_logs_manager.get = AsyncMock(side_effect=LogFetchError)

        # When...
        with raises(LogFetchError):
            await member_manager.get_logs(sample_member.id)

        # Expect device_logs_manager.get to be called
        mock_device_logs_manager.get.assert_called_once()

    async def test_not_found(
        self,
        mock_member_repository: MemberRepository,
        sample_member,
        member_manager: MemberManager,
    ):
        # Given...
        mock_member_repository.get_by_id = AsyncMock(return_value=(None))

        # When...
        with raises(MemberNotFoundError):
            await member_manager.get_logs(sample_member.username)


@fixture
def sample_mutation_request(faker):
    return AbstractMember(
        username=faker.user_name(),
        email=faker.email(),
        firstName=faker.first_name(),
        lastName=faker.last_name(),
        departureDate=faker.date_this_year(after_today=True).isoformat(),
        comment=faker.sentence(),
    )


@fixture
def mock_device_logs_manager():
    return MagicMock(spec=DeviceLogsManager)


@fixture
def mock_device_ip_manager():
    return MagicMock(spec=DeviceIpManager)


@fixture
def member_manager(
    mock_member_repository,
    subscription_manager,
    mock_mailinglist_repository,
    mock_device_logs_manager,
    mock_device_ip_manager,
    mock_room_repository,
):
    return MemberManager(
        member_repository=mock_member_repository,
        device_ip_manager=mock_device_ip_manager,
        device_logs_manager=mock_device_logs_manager,
        mailinglist_repository=mock_mailinglist_repository,
        subscription_manager=subscription_manager,
        room_repository=mock_room_repository,
    )


@fixture
def subscription_manager(
    mock_member_repository,
    mock_membership_repository,
    mock_charter_repository,
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
    )


@fixture
def mock_mailinglist_repository():
    return MagicMock(spec=MailinglistRepository)


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
def mock_member_repository():
    return MagicMock(spec=MemberRepository)


@fixture
def mock_membership_repository():
    return MagicMock(spec=MembershipRepository)


@fixture
def mock_charter_repository():
    return MagicMock(spec=CharterRepository)


@fixture
def mock_logs_repository():
    r = MagicMock(spec=LogsRepository)
    r.get_logs = AsyncMock(return_value=[FAKE_LOGS_OBJ])
    return r


@fixture
def mock_device_repository():
    return MagicMock(spec=DeviceRepository)


@fixture
def sample_subscription_pending_rules(sample_member):
    return Membership(uuid="", member=sample_member, status=MembershipStatus.PENDING_RULES.value, hasRoom=False)


@fixture
def mock_ip_allocator():
    return MagicMock(spec=IpAllocator)


@fixture
def mock_vlan_repository():
    return MagicMock(spec=VlanRepository)


@fixture
def mock_room_repository():
    return MagicMock(spec=RoomRepository)


@fixture
def sample_subscription_pending_payment_initial(sample_member):
    return Membership(
        uuid="",
        member=sample_member,
        status=MembershipStatus.PENDING_PAYMENT_INITIAL.value,
        hasRoom=sample_member.room_number is not None,
    )


@fixture
def sample_subscription_pending_payment(sample_member):
    return Membership(
        uuid="",
        member=sample_member,
        status=MembershipStatus.PENDING_PAYMENT.value,
        duration=MembershipDuration.ONE_YEAR.value,
        hasRoom=sample_member.room_number is not None,
    )


@fixture
def sample_subscription_pending_payment_validation(sample_member, sample_payment_method):
    return Membership(
        uuid="",
        member=sample_member,
        status=MembershipStatus.PENDING_PAYMENT_VALIDATION.value,
        duration=MembershipDuration.ONE_YEAR.value,
        paymentMethod=sample_payment_method.id,
        hasRoom=sample_member.room_number is not None,
    )


@fixture
def sample_membership_pending_rules(sample_member):
    return Membership(
        uuid="",
        member=sample_member,
        status=MembershipStatus.PENDING_RULES.value,
        hasRoom=sample_member.room_number is not None,
    )


@fixture
def sample_membership_pending_payment_initial(sample_member):
    return Membership(
        uuid="",
        member=sample_member,
        status=MembershipStatus.PENDING_PAYMENT_INITIAL.value,
        hasRoom=sample_member.room_number is not None,
    )


@fixture
def sample_membership_pending_payment(sample_member):
    return Membership(
        uuid="",
        member=sample_member,
        status=MembershipStatus.PENDING_PAYMENT.value,
        duration=MembershipDuration.ONE_YEAR.value,
        hasRoom=sample_member.room_number is not None,
    )


@fixture
def sample_membership_pending_payment_validation(sample_member, sample_payment_method):
    return Membership(
        uuid="",
        member=sample_member,
        status=MembershipStatus.PENDING_PAYMENT_VALIDATION.value,
        duration=MembershipDuration.ONE_YEAR.value,
        paymentMethod=sample_payment_method.id,
        hasRoom=sample_member.room_number is not None,
    )


@fixture
def mock_netbox_repository():
    return AsyncMock(spec=NetboxRepository)


@fixture
def member_manager_with_netbox(
    mock_member_repository,
    subscription_manager,
    mock_mailinglist_repository,
    mock_device_logs_manager,
    mock_device_ip_manager,
    mock_room_repository,
    mock_netbox_repository,
):
    return MemberManager(
        member_repository=mock_member_repository,
        device_ip_manager=mock_device_ip_manager,
        device_logs_manager=mock_device_logs_manager,
        mailinglist_repository=mock_mailinglist_repository,
        subscription_manager=subscription_manager,
        room_repository=mock_room_repository,
        netbox_repository=mock_netbox_repository,
    )


class TestNetboxIntegration:
    async def test_update_subnet_calls_create_wifi_prefix(
        self,
        member_manager_with_netbox: MemberManager,
        mock_member_repository: MagicMock,
        mock_device_ip_manager: MagicMock,
        mock_netbox_repository: AsyncMock,
        sample_member: Member,
    ):
        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)
        mock_member_repository.used_wireless_public_ips = AsyncMock(return_value=[])
        mock_member_repository.update = AsyncMock(return_value=sample_member)
        mock_device_ip_manager.allocate_ips = AsyncMock(return_value=None)

        await member_manager_with_netbox.update_subnet(sample_member.id)

        mock_netbox_repository.create_wifi_prefix.assert_called_once()
        call_args = mock_netbox_repository.create_wifi_prefix.call_args
        assert call_args.args[1] == sample_member.id

    async def test_reset_member_calls_delete_wifi_prefix(
        self,
        member_manager_with_netbox: MemberManager,
        mock_member_repository: MagicMock,
        mock_device_ip_manager: MagicMock,
        mock_netbox_repository: AsyncMock,
        sample_member: Member,
    ):
        sample_member.subnet = "192.168.42.0/28"
        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)
        mock_member_repository.update = AsyncMock(return_value=sample_member)
        mock_device_ip_manager.unallocate_ips = AsyncMock(return_value=None)

        await member_manager_with_netbox.reset_member(sample_member.id)

        mock_netbox_repository.delete_wifi_prefix.assert_called_once_with("192.168.42.0/28")

    async def test_netbox_none_does_not_break_update_subnet(
        self,
        member_manager: MemberManager,
        mock_member_repository: MagicMock,
        mock_device_ip_manager: MagicMock,
        sample_member: Member,
    ):
        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)
        mock_member_repository.used_wireless_public_ips = AsyncMock(return_value=[])
        mock_member_repository.update = AsyncMock(return_value=sample_member)
        mock_device_ip_manager.allocate_ips = AsyncMock(return_value=None)

        # Should not raise even with netbox_repository=None
        await member_manager.update_subnet(sample_member.id)
