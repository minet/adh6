# coding=utf-8 import datetime import datetime import datetime
import datetime
from dataclasses import asdict
from unittest import mock
from unittest.mock import MagicMock

from pytest import fixture, raises, mark

from config import TEST_CONFIGURATION
from src.entity import AbstractMember
from src.entity.member import Member
from src.exceptions import LogFetchError, NoPriceAssignedToThatDuration, MemberNotFoundError, UsernameMismatchError, \
    PasswordTooShortError, IntMustBePositive, MissingRequiredField, UnknownPaymentMethod, InvalidAdmin
from src.use_case.interface.device_repository import DeviceRepository
from src.use_case.interface.logs_repository import LogsRepository
from src.use_case.interface.member_repository import MemberRepository
from src.use_case.interface.membership_repository import MembershipRepository
from src.use_case.interface.money_repository import MoneyRepository
from src.use_case.member_manager import MemberManager, FullMutationRequest, PartialMutationRequest
from src.util.hash import ntlm_hash

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

FAKE_LOGS = "blah blah blah logging logs"


class TestNewMembership:
    def test_happy_path(self, ctx,
                        faker,
                        mock_membership_repository: MagicMock,
                        mock_member_repository: MagicMock,
                        sample_member,
                        member_manager: MemberManager):
        test_date = faker.date_time_this_year()
        # When...
        member_manager.new_membership(ctx, sample_member.username, 1, 'cash', start_str=test_date.isoformat())

        # Expect...
        expected_start_date = test_date
        expected_end_date = test_date + datetime.timedelta(days=1)

        # Expect to create a new membership record...
        self._assert_membership_record_was_created(ctx, sample_member.username, mock_membership_repository,
                                                   expected_start_date, expected_end_date)

    def test_happy_path_without_start_time(self, ctx,
                                           faker,
                                           sample_member,
                                           mock_membership_repository: MagicMock,
                                           mock_member_repository: MagicMock,
                                           member_manager: MemberManager):
        test_date = faker.date_time_this_year()
        # Given that now == TEST_DATE (monkey patch datetime.now())
        # See here: http://blog.xelnor.net/python-mocking-datetime/
        with mock.patch.object(datetime, 'datetime', mock.Mock(wraps=datetime.datetime)) as patched:
            patched.now.return_value = test_date

            # When...
            member_manager.new_membership(ctx, sample_member.username, 1, 'card')

        # Expect...
        expected_start_date = test_date
        expected_end_date = test_date + datetime.timedelta(days=1)

        # Expect to create a new membership record...
        self._assert_membership_record_was_created(ctx, sample_member.username, mock_membership_repository,
                                                   expected_start_date, expected_end_date)

    def test_invalid_duration(self, ctx,
                              sample_member,
                              mock_member_repository: MagicMock,
                              mock_membership_repository: MagicMock,
                              member_manager: MemberManager):
        # When...
        with raises(IntMustBePositive):
            member_manager.new_membership(ctx, sample_member.username, -1, 'bank_cheque')

        # Expect that the database has not been touched.
        mock_member_repository.update.assert_not_called()
        mock_membership_repository.create_membership.assert_not_called()

    def test_no_price_for_duration(self, ctx,
                                   sample_member,
                                   mock_member_repository: MagicMock,
                                   mock_membership_repository: MagicMock,
                                   member_manager: MemberManager):
        # When...
        with raises(NoPriceAssignedToThatDuration):
            member_manager.new_membership(ctx, sample_member.username, 123456789, 'cash')

        # Expect that the database has not been touched.
        mock_member_repository.update.assert_not_called()
        mock_membership_repository.create_membership.assert_not_called()

    @mark.parametrize('exception', [UnknownPaymentMethod, InvalidAdmin])
    def test_fail_to_create_transaction(self, ctx,
                                        faker,
                                        sample_member,
                                        mock_membership_repository: MembershipRepository,
                                        mock_member_repository: MemberRepository,
                                        mock_money_repository: MoneyRepository,
                                        exception: Exception,
                                        member_manager: MemberManager):
        mock_member_repository.update_member = MagicMock()
        mock_money_repository.add_member_payment_record = MagicMock(side_effect=exception)
        test_date = faker.date_time_this_year()

        # When...
        with raises(exception):
            member_manager.new_membership(ctx, sample_member.username, 1, 'cash', start_str=test_date.isoformat())

        # Expect...
        mock_member_repository.update_member.assert_not_called()

    @staticmethod
    def _assert_membership_record_was_created(ctx, user, repo, start_time, end_time):
        repo.create_membership.assert_called_once_with(
            ctx,
            user,
            start_time,
            end_time
        )


class TestGetByID:
    def test_happy_path(self, ctx,
                        mock_member_repository: MagicMock,
                        sample_member: Member,
                        member_manager: MemberManager):
        # Given...
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))

        # When...
        result = member_manager.get_by_id(ctx, member_id=sample_member.id)

        # Expect...
        assert sample_member == result
        mock_member_repository.search_by.assert_called_once_with(ctx, filter_=AbstractMember(id=sample_member.id))

    def test_not_found(self, ctx,
                       sample_member,
                       mock_member_repository: MagicMock,
                       member_manager: MemberManager):
        # Given...
        mock_member_repository.search_by = MagicMock(return_value=([], 0))

        # When...
        with raises(MemberNotFoundError):
            member_manager.get_by_id(ctx, member_id=sample_member.id)

        # Expect...
        mock_member_repository.search_by.assert_called_once_with(ctx, filter_=AbstractMember(id=sample_member.id))


class TestSearch:
    def test_happy_path(self, ctx,
                        mock_member_repository: MagicMock,
                        sample_member: Member,
                        member_manager: MemberManager):
        # Given...
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))

        # When...
        test_terms = 'blah blah blah'
        test_offset = 42
        test_limit = 99
        result, count = member_manager.search(ctx, limit=test_limit, offset=test_offset, terms=test_terms)

        # Expect...
        assert [sample_member] == result

        # Make sure that all the parameters are passed to the DB.
        mock_member_repository.search_by.assert_called_once_with(ctx,
                                                                 limit=test_limit,
                                                                 offset=test_offset,
                                                                 filter_=None,
                                                                 terms=test_terms)

    def test_invalid_limit(self, ctx,
                           member_manager: MemberManager):
        # When...
        with raises(IntMustBePositive):
            member_manager.search(ctx, limit=-1)

    def test_invalid_offset(self, ctx,
                            member_manager: MemberManager):
        # When...
        with raises(IntMustBePositive):
            member_manager.search(ctx, limit=10, offset=-1)


class TestCreateOrUpdate:

    def test_create_happy_path(self, ctx,
                               mock_member_repository: MagicMock,
                               sample_member,
                               sample_mutation_request: FullMutationRequest,
                               member_manager: MemberManager):
        # Given that there is not user in the DB (user will be created).
        mock_member_repository.search_by = MagicMock(return_value=([], 0))

        # When...
        member_manager.update_or_create(ctx, sample_mutation_request)

        # Expect...
        mock_member_repository.create.assert_called_once_with(ctx, sample_mutation_request)

    def test_update_happy_path(self, ctx,
                               mock_member_repository: MagicMock,
                               sample_mutation_request: FullMutationRequest,
                               sample_member: Member,
                               member_manager: MemberManager):
        # Given that there is a user in the DB (user will be updated).
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))

        # Given a request that updates some fields.
        req = sample_mutation_request
        req.comment = "Updated comment."
        req.first_name = "George"
        req.last_name = "Dupuis"

        # When...
        member_manager.update_or_create(ctx, req, member_id=sample_member.id)

        # Expect...
        mock_member_repository.update.assert_called_once_with(ctx, req, override=True)
        mock_member_repository.create.assert_not_called()  # Do not create any member!


class TestUpdatePartially:
    def test_happy_path(self, ctx,
                        mock_member_repository: MagicMock,
                        sample_member,
                        member_manager: MemberManager):
        updated_comment = 'Updated comment.'
        req = PartialMutationRequest(comment=updated_comment)

        # When...
        member_manager.partially_update(ctx, req, member_id=sample_member.id)

        # Expect...
        mock_member_repository.update.assert_called_once_with(ctx, req, override=False)

    def test_not_found(self, ctx,
                       mock_member_repository: MagicMock,
                       sample_member,
                       member_manager: MemberManager):
        mock_member_repository.update = MagicMock(side_effect=MemberNotFoundError)

        # When...
        with raises(MemberNotFoundError):
            member_manager.partially_update(ctx, AbstractMember(id=sample_member.id), member_id=sample_member.id)


class TestDelete:
    def test_happy_path(self, ctx,
                        mock_member_repository: MagicMock,
                        sample_member,
                        member_manager: MemberManager):
        # When...
        member_manager.delete(ctx, member_id=sample_member.id)

        # Expect...
        mock_member_repository.delete.assert_called_once_with(ctx, sample_member.id)

    def test_not_found(self, ctx,
                       mock_member_repository: MagicMock,
                       sample_member,
                       member_manager: MemberManager):
        # Given...
        mock_member_repository.delete = MagicMock(side_effect=MemberNotFoundError)

        # When...
        with raises(MemberNotFoundError):
            member_manager.delete(ctx, member_id=sample_member.id)


class TestGetLogs:
    def test_happy_path(self, ctx,
                        mock_logs_repository: MagicMock,
                        mock_member_repository: MagicMock,
                        mock_device_repository: MagicMock,
                        sample_member: Member,
                        member_manager: MemberManager):
        # Given...
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))

        # When...
        result = member_manager.get_logs(ctx, sample_member.username)

        # Expect...
        assert FAKE_LOGS == result
        devices = mock_device_repository.search_by(ctx, username=sample_member.username)
        mock_logs_repository.get_logs.assert_called_once_with(ctx, devices=devices.__getitem__(),
                                                              username=sample_member.username, dhcp=False)

    def test_fetch_failed(self, ctx,
                          mock_logs_repository: MagicMock,
                          mock_member_repository: MagicMock,
                          sample_member: Member,
                          member_manager: MemberManager):
        # Given...
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))
        mock_logs_repository.get_logs = MagicMock(side_effect=LogFetchError)

        # When...
        result = member_manager.get_logs(ctx, sample_member.username)

        # Expect use case to 'fail open', do not throw any error, assume there is no log.
        assert [] == result

    def test_not_found(self, ctx,
                       mock_member_repository: MagicMock,
                       sample_member,
                       member_manager: MemberManager):
        # Given...
        mock_member_repository.search_by = MagicMock(return_value=([], 0))

        # When...
        with raises(MemberNotFoundError):
            member_manager.get_logs(ctx, sample_member.username)


@fixture
def sample_mutation_request(faker, sample_room):
    return AbstractMember(
        username=faker.user_name,
        email=faker.email,
        first_name=faker.first_name,
        last_name=faker.last_name,
        departure_date=faker.date_this_year(after_today=True).isoformat(),
        comment=faker.sentence,
        association_mode=faker.date_time_this_year(after_now=True).isoformat(),
        room=sample_room,
    )


@fixture
def member_manager(
        mock_member_repository,
        mock_money_repository,
        mock_membership_repository,
        mock_logs_repository,
        mock_device_repository,
):
    return MemberManager(
        member_repository=mock_member_repository,
        money_repository=mock_money_repository,
        membership_repository=mock_membership_repository,
        logs_repository=mock_logs_repository,
        device_repository=mock_device_repository,
        configuration=TEST_CONFIGURATION,
    )


@fixture
def mock_money_repository():
    return MagicMock(spec=MoneyRepository)


@fixture
def mock_member_repository():
    return MagicMock(spec=MemberRepository)


@fixture
def mock_membership_repository():
    return MagicMock(spec=MembershipRepository)


@fixture
def mock_logs_repository():
    r = MagicMock(spec=LogsRepository)
    r.get_logs = MagicMock(return_value=FAKE_LOGS)
    return r


@fixture
def mock_device_repository():
    return MagicMock(spec=DeviceRepository)
