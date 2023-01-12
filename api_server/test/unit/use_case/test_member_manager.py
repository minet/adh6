# coding=utf-8 import datetime import datetime import datetime
import pytest
from unittest.mock import MagicMock

from pytest import fixture, raises

from adh6.member import MembershipDuration, MembershipStatus, MemberManager, SubscriptionManager
from adh6.entity import AbstractMember, Member, Membership, MemberBody
from adh6.exceptions import AccountTypeNotFoundError, LogFetchError, MemberAlreadyExist, MemberNotFoundError
from adh6.device import DeviceIpManager, DeviceLogsManager
from adh6.device.interfaces import IpAllocator, LogsRepository, DeviceRepository
from adh6.member.interfaces import MemberRepository, MembershipRepository
from adh6.member import MailinglistManager
from adh6.treasury import AccountManager, AccountTypeManager
from adh6.room.interfaces import RoomRepository
from adh6.subnet.interfaces import VlanRepository
from test import SAMPLE_CLIENT

INVALID_MUTATION_REQ_ARGS = [
    ('empty_email', {'email': ''}),
    ('empty_first_name', {'first_name': ''}),
    ('empty_last_name', {'last_name': ''}),
    ('empty_username', {'username': ''}),
    ('empty_room_number', {'room_number': ''}),

    ('invalid_email', {'email': 'not a valid email'}),
    ('invalid_username', {'username': 'this username is way too long'}),

    ('invalid_association_mode', {'association_mode': 'this is not a date'}),
    ('invalid_departure_date', {'departure_date': 'this is not a date'}),
]

FAKE_LOGS_OBJ = [1, "blah blah blah logging logs"]
FAKE_LOGS = "1  "


class TestProfile:
    def test_happy_path(self,
                        mock_member_repository: MemberRepository,
                        mock_subscription_manager: SubscriptionManager,
                        sample_member: Member,
                        member_manager: MemberManager):
        mock_member_repository.get_by_login = MagicMock(return_value=(sample_member))
        mock_subscription_manager.latest = MagicMock(return_value=(None))
        m, _ = member_manager.get_profile()
        assert sample_member == m
        mock_member_repository.get_by_login.assert_called_once()

    def test_member_not_found(self,
                        mock_member_repository: MemberRepository,
                        member_manager: MemberManager,
                        sample_member: Member):
        mock_member_repository.get_by_login = MagicMock(return_value=(None), side_effect=MemberNotFoundError(""))
        with pytest.raises(MemberNotFoundError):
            member_manager.get_profile()
        mock_member_repository.get_by_login.assert_called_once_with(sample_member.username)


class TestGetByID:
    def test_happy_path(self,
                        mock_member_repository: MemberRepository,
                        mock_membership_repository: MembershipRepository,
                        mock_subscription_manager: SubscriptionManager,
                        sample_member: Member,
                        member_manager: MemberManager):
        # Given...
        mock_member_repository.get_by_id = MagicMock(return_value=(sample_member))
        mock_membership_repository.search = MagicMock(return_value=([], 0))
        mock_subscription_manager.latest = MagicMock(return_value=(None))

        # When...
        result = member_manager.get_by_id(id=sample_member.id)

        # Expect...
        assert sample_member == result
        mock_member_repository.get_by_id.assert_called_once_with(sample_member.id)

    def test_not_found(self,
                       sample_member,
                       mock_member_repository: MemberRepository,
                       member_manager: MemberManager):
        # Given...
        mock_member_repository.get_by_id = MagicMock(return_value=(None), side_effect=MemberNotFoundError(""))

        # When...
        with raises(MemberNotFoundError):
            member_manager.get_by_id(id=sample_member.id)

        # Expect...
        mock_member_repository.get_by_id.assert_called_once_with(sample_member.id)


class TestSearch:
    def test_happy_path(self,
                        mock_member_repository: MemberRepository,
                        sample_member: Member,
                        member_manager: MemberManager):
        # Given...
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))

        # When...
        test_terms = 'blah blah blah'
        test_offset = 42
        test_limit = 99
        result, _ = member_manager.search(limit=test_limit, offset=test_offset, terms=test_terms)

        # Expect...
        assert [sample_member.id] == result

        # Make sure that all the parameters are passed to the DB.
        mock_member_repository.search_by.assert_called_once_with(limit=test_limit, offset=test_offset, terms=test_terms, filter_=None)


class TestNewMember:
    def test_member_already_exist(self,
                        mock_member_repository: MemberRepository,
                        sample_member: AbstractMember,
                        member_manager: MemberManager):
        # Given...
        mock_member_repository.get_by_login = MagicMock(return_value=(sample_member))

        # When...
        with pytest.raises(MemberAlreadyExist):
            member_manager.create(body=MemberBody(username=sample_member.username))

        # Expect...
        mock_member_repository.get_by_login.assert_called_once_with(sample_member.username)

    def test_no_account_type_adherent(self,
                        mock_member_repository: MemberRepository,
                        mock_account_type_manager: AccountTypeManager,
                        member_manager: MemberManager):
        # Given...
        mock_member_repository.get_by_login = MagicMock(return_value=(None))
        mock_account_type_manager.search = MagicMock(return_value=([], 0))

        # When...
        with pytest.raises(AccountTypeNotFoundError):
            member_manager.create(body=MemberBody(
                                      username="testtest",
                                  ))

        # Expect...
        mock_account_type_manager.search.assert_called_once_with(terms="Adhérent")


class TestCreateOrUpdate:

    def test_create_happy_path(self,
                               mock_member_repository: MagicMock,
                               sample_mutation_request: AbstractMember,
                               member_manager: MemberManager):
        # Given that there is not user in the DB (user will be created).
        mock_member_repository.search_by = MagicMock(return_value=([], 0))

        # When...
        member_manager.update_or_create(sample_mutation_request)

        # Expect...
        mock_member_repository.create.assert_called_once_with(sample_mutation_request)

    def test_update_happy_path(self,
                               mock_member_repository: MemberRepository,
                               sample_mutation_request: AbstractMember,
                               mock_subscription_manager: SubscriptionManager,
                               sample_member: Member,
                               member_manager: MemberManager):
        # Given that there is a user in the DB (user will be updated).
        mock_member_repository.get_by_id = MagicMock(return_value=(sample_member))
        mock_subscription_manager.latest = MagicMock(return_value=(None))

        # Given a request that updates some fields.
        req = sample_mutation_request
        req.comment = "Updated comment."
        req.first_name = "George"
        req.last_name = "Dupuis"

        # When...
        member_manager.update_or_create(req, id=sample_member.id)

        # Expect...
        mock_member_repository.update.assert_called_once_with(req, override=True)
        mock_member_repository.create.assert_not_called()  # Do not create any member!


class TestUpdatePartially:
    def test_happy_path(self,
                        mock_member_repository: MagicMock,
                        sample_member,
                        member_manager: MemberManager):
        updated_comment = 'Updated comment.'
        req = AbstractMember(comment=updated_comment)

        # When...
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))
        member_manager.partially_update(req, id=sample_member.id)

        # Expect...
        mock_member_repository.update.assert_called_once_with(req, override=False)

    def test_not_found(self,
                       mock_member_repository: MagicMock,
                       sample_member,
                       member_manager: MemberManager):
        mock_member_repository.search_by = MagicMock(return_value=([], 0))
        mock_member_repository.update = MagicMock(side_effect=MemberNotFoundError)

        # When...
        with raises(MemberNotFoundError):
            member_manager.partially_update(AbstractMember(id=sample_member.id), id=sample_member.id)


class TestDelete:
    def test_happy_path(self,
                        mock_member_repository: MagicMock,
                        sample_member,
                        member_manager: MemberManager):
        # When...
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))
        member_manager.delete(id=sample_member.id)

        # Expect...
        mock_member_repository.delete.assert_called_once_with(sample_member.id)

    def test_not_found(self,
                       mock_member_repository: MagicMock,
                       sample_member,
                       member_manager: MemberManager):
        # Given...
        mock_member_repository.search_by = MagicMock(return_value=([], 0))
        mock_member_repository.delete = MagicMock(side_effect=MemberNotFoundError)

        # When...
        with raises(MemberNotFoundError):
            member_manager.delete(id=sample_member.id)


@fixture
def sample_mutation_request(faker):
    return AbstractMember(
        id=0,
        username=faker.user_name(),
        email=faker.email(),
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        departure_date=faker.date_this_year(after_today=True).isoformat(),
        comment=faker.sentence(),
    )


@fixture
def mock_device_ip_manager():
    return MagicMock(spec=DeviceIpManager)


@fixture
def member_manager(
        mock_member_repository,
        mock_account_manager,
        mock_account_type_manager,
        mock_subscription_manager,
        mock_mailinglist_manager,
        mock_device_ip_manager,
):
    return MemberManager(
        member_repository=mock_member_repository,
        account_manager=mock_account_manager,
        account_type_manager=mock_account_type_manager,
        device_ip_manager=mock_device_ip_manager,
        mailinglist_manager=mock_mailinglist_manager,
        subscription_manager=mock_subscription_manager
    )


@fixture
def mock_subscription_manager():
    return MagicMock(spec=SubscriptionManager)


@fixture
def mock_mailinglist_manager():
    return MagicMock(spec=MailinglistManager)


@fixture
def mock_account_manager():
    return MagicMock(spec=AccountManager)


@fixture
def mock_account_type_manager():
    return MagicMock(spec=AccountTypeManager)


@fixture
def mock_member_repository():
    return MagicMock(spec=MemberRepository)


@fixture
def mock_membership_repository():
    return MagicMock(spec=MembershipRepository)


@fixture
def mock_device_repository():
    return MagicMock(spec=DeviceRepository)

@fixture
def sample_subscription_pending_rules(sample_member):
    return Membership(
        uuid="",
        member=sample_member,
        status=MembershipStatus.PENDING_RULES.value
    )
    
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
        status=MembershipStatus.PENDING_PAYMENT_INITIAL.value
    )

@fixture
def sample_subscription_pending_payment(sample_member):
    return Membership(
        uuid="",
        member=sample_member,
        status=MembershipStatus.PENDING_PAYMENT.value,
        duration=MembershipDuration.ONE_YEAR.value
    )

@fixture
def sample_subscription_pending_payment_validation(sample_member, sample_account1, sample_payment_method):
    return Membership(
        uuid="",
        member=sample_member,
        status=MembershipStatus.PENDING_PAYMENT_VALIDATION.value,
        duration=MembershipDuration.ONE_YEAR.value,
        account=sample_account1.id,
        payment_method=sample_payment_method.id
    )

@fixture
def sample_membership_pending_rules(sample_member):
    return Membership(
        uuid="",
        member=sample_member,
        status=MembershipStatus.PENDING_RULES.value,
    )

@fixture
def sample_membership_pending_payment_initial(sample_member):
    return Membership(
        uuid="",
        member=sample_member,
        status=MembershipStatus.PENDING_PAYMENT_INITIAL.value,
    )

@fixture
def sample_membership_pending_payment(sample_member):
    return Membership(
        uuid="",
        member=sample_member,
        status=MembershipStatus.PENDING_PAYMENT.value,
        duration=MembershipDuration.ONE_YEAR.value,
    )

@fixture
def sample_membership_pending_payment_validation(sample_member, sample_account1, sample_payment_method):
    return Membership(
        uuid="",
        member=sample_member,
        status=MembershipStatus.PENDING_PAYMENT_VALIDATION.value,
        duration=MembershipDuration.ONE_YEAR.value,
        account=sample_account1.id,
        payment_method=sample_payment_method.id,
    )
