# coding=utf-8 import datetime import datetime import datetime
import datetime
from unittest import mock

import pytest
from src.use_case.interface.payment_method_repository import PaymentMethodRepository
from src.use_case.interface.transaction_repository import TransactionRepository
from src.use_case.interface.account_type_repository import AccountTypeRepository
from src.use_case.interface.account_repository import AccountRepository
from unittest.mock import MagicMock

from pytest import fixture, raises

from src.constants import DEFAULT_LIMIT, DEFAULT_OFFSET, MembershipStatus
from src.entity import AbstractMember, Member, Membership, Account, PaymentMethod
from src.exceptions import AccountNotFoundError, LogFetchError, MembershipNotFoundError, MembershipStatusNotAllowed, MemberNotFoundError, IntMustBePositive, NoPriceAssignedToThatDuration, PaymentMethodNotFoundError
from src.use_case.interface.device_repository import DeviceRepository
from src.use_case.interface.logs_repository import LogsRepository
from src.use_case.interface.member_repository import MemberRepository
from src.use_case.interface.membership_repository import MembershipRepository
from src.use_case.member_manager import MemberManager
from src.use_case.device_manager import DeviceManager
from src.use_case.interface.ip_allocator import IpAllocator

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
FAKE_LOGS = "1 blah blah blah logging logs"


class TestNewMembership:
    """Unit tests for the management of the memberships
    """
    def test_member_not_found(self, ctx,
                        mock_member_repository: MagicMock,
                        sample_member: Member,
                        sample_membership_empty: Membership,
                        member_manager: MemberManager):
        mock_member_repository.search_by = MagicMock(return_value=([], 0))
        # When...
        with pytest.raises(MemberNotFoundError):
            member_manager.new_membership(ctx, sample_member.id, sample_membership_empty)

    def test_pending_rules(self, ctx,
                        mock_membership_repository: MagicMock,
                        mock_member_repository: MagicMock,
                        sample_member: Member,
                        sample_membership_empty: Membership,
                        member_manager: MemberManager):
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))
        mock_membership_repository.membership_search_by = MagicMock(return_value=([], 0))
        mock_member_repository.get_charter = MagicMock(return_value="")
        # When...
        member_manager.new_membership(ctx, sample_member.id, sample_membership_empty)


        # Expect to create a new membership record...
        mock_membership_repository.create_membership.assert_called_once_with(
            ctx,
            sample_member.id,
            sample_membership_empty
        )

        assert sample_membership_empty.status == MembershipStatus.PENDING_RULES.value
    
    def test_pending_payment_initial(self, ctx,
                        mock_membership_repository: MagicMock,
                        mock_member_repository: MagicMock,
                        sample_member: Member,
                        sample_membership_empty: Membership,
                        member_manager: MemberManager):
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))
        mock_membership_repository.membership_search_by = MagicMock(return_value=([], 0))
        mock_member_repository.get_charter = MagicMock(return_value=str(datetime.datetime.today()))
        # When...
        member_manager.new_membership(ctx, sample_member.id, sample_membership_empty)

        # Expect to create a new membership record...
        mock_membership_repository.create_membership.assert_called_once_with(
            ctx,
            sample_member.id,
            sample_membership_empty
        )
        
        assert sample_membership_empty.status == MembershipStatus.PENDING_PAYMENT_INITIAL.value

    def test_pending_payment(self, ctx,
                        mock_membership_repository: MagicMock,
                        mock_member_repository: MagicMock,
                        sample_member: Member,
                        sample_membership_duration_no_account: Membership,
                        member_manager: MemberManager):
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))
        mock_membership_repository.membership_search_by = MagicMock(return_value=([], 0))
        mock_member_repository.get_charter = MagicMock(return_value=str(datetime.datetime.today()))
        # When...
        member_manager.new_membership(ctx, sample_member.id, sample_membership_duration_no_account)

        # Expect to create a new membership record...
        mock_membership_repository.create_membership.assert_called_once_with(
            ctx,
            sample_member.id,
            sample_membership_duration_no_account
        )
        
        assert sample_membership_duration_no_account.status == MembershipStatus.PENDING_PAYMENT.value

    def test_payment_validation(self, ctx,
                        mock_membership_repository: MagicMock,
                        mock_member_repository: MagicMock,
                        mock_account_repository: MagicMock,
                        mock_payment_method_repository: MagicMock,
                        sample_member: Member,
                        sample_membership_duration_account_payment_method: Membership,
                        sample_account1: Account,
                        sample_payment_method: PaymentMethod,
                        member_manager: MemberManager):
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))
        mock_membership_repository.membership_search_by = MagicMock(return_value=([], 0))
        mock_account_repository.search_by = MagicMock(return_value=([sample_account1], 1))
        mock_payment_method_repository.search_by = MagicMock(return_value=([sample_payment_method], 1))
        mock_member_repository.get_charter = MagicMock(return_value=str(datetime.datetime.today()))
        # When...
        member_manager.new_membership(ctx, sample_member.id, sample_membership_duration_account_payment_method)

        # Expect to create a new membership record...
        mock_membership_repository.create_membership.assert_called_once_with(
            ctx,
            sample_member.id,
            sample_membership_duration_account_payment_method
        )
        
        assert sample_membership_duration_account_payment_method.status == MembershipStatus.PENDING_PAYMENT_VALIDATION.value

    def test_bad_initial_status(self, ctx,
                        mock_member_repository: MagicMock,
                        sample_membership_empty: Membership,
                        sample_member: Member,
                        member_manager: MemberManager):
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))
        sample_membership_empty.status = MembershipStatus.COMPLETE.value

        with raises(MembershipStatusNotAllowed):
            member_manager.new_membership(ctx, sample_member.id, sample_membership_empty)

    def test_membership_already_pending(self, ctx,
                        mock_member_repository: MagicMock,
                        sample_membership_empty: Membership,
                        sample_member: Member,
                        member_manager: MemberManager):
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))
        sample_membership_empty.status = MembershipStatus.COMPLETE.value

        with raises(MembershipStatusNotAllowed):
            member_manager.new_membership(ctx, sample_member.id, sample_membership_empty)

    def test_unknown_member(self, ctx,
                        mock_member_repository: MagicMock,
                        sample_membership_empty: Membership,
                        sample_member: Member,
                        member_manager: MemberManager):
        mock_member_repository.search_by = MagicMock(return_value=([], 1))

        with raises(MemberNotFoundError):
            member_manager.new_membership(ctx, sample_member.id, sample_membership_empty)

    def test_unknown_account(self, ctx,
                        mock_membership_repository: MagicMock,
                        mock_member_repository: MagicMock,
                        mock_account_repository: MagicMock,
                        sample_member: Member,
                        sample_membership_duration_account_payment_method: Membership,
                        member_manager: MemberManager):
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))
        mock_membership_repository.membership_search_by = MagicMock(return_value=([], 0))
        mock_account_repository.search_by = MagicMock(return_value=([], 0))
        mock_member_repository.get_charter = MagicMock(return_value=str(datetime.datetime.today()))

        with raises(AccountNotFoundError):
            member_manager.new_membership(ctx, sample_member.id, sample_membership_duration_account_payment_method)

    def test_unknown_payment_method(self, ctx,
                        mock_membership_repository: MagicMock,
                        mock_member_repository: MagicMock,
                        mock_account_repository: MagicMock,
                        mock_payment_method_repository: MagicMock,
                        sample_member: Member,
                        sample_membership_duration_account_payment_method: Membership,
                        sample_account1: Account,
                        member_manager: MemberManager):
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))
        mock_membership_repository.membership_search_by = MagicMock(return_value=([], 0))
        mock_account_repository.search_by = MagicMock(return_value=([sample_account1], 1))
        mock_payment_method_repository.search_by = MagicMock(return_value=([], 0))
        mock_member_repository.get_charter = MagicMock(return_value=str(datetime.datetime.today()))

        with raises(PaymentMethodNotFoundError):
            member_manager.new_membership(ctx, sample_member.id, sample_membership_duration_account_payment_method)

    def test_unknown_price_asign_to_duration(self, ctx,
                        mock_membership_repository: MagicMock,
                        mock_member_repository: MagicMock,
                        sample_member: Member,
                        sample_membership_empty: Membership,
                        member_manager: MemberManager):
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))
        mock_membership_repository.membership_search_by = MagicMock(return_value=([], 0))
        mock_member_repository.get_charter = MagicMock(return_value=str(datetime.datetime.today()))
        sample_membership_empty.duration = 12

        with raises(NoPriceAssignedToThatDuration):
            member_manager.new_membership(ctx, sample_member.id, sample_membership_empty)


class TestPatchMembership:
    def test_from_pending_rules_to_pending_payment_initial(self, ctx,
                        mock_membership_repository: MagicMock,
                        mock_member_repository: MagicMock,
                        sample_member: Member,
                        sample_membership_pending_rules: Membership,
                        sample_membership_empty: Membership,
                        member_manager: MemberManager):
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))
        mock_membership_repository.membership_search_by = MagicMock(return_value=([sample_membership_pending_rules], 1))
        mock_member_repository.get_charter = MagicMock(return_value=str(datetime.datetime.today()))
        # When...
        member_manager.change_membership(ctx, sample_member.id, sample_membership_pending_rules.uuid, sample_membership_empty)

        # Expect to create a new membership record...
        mock_membership_repository.update_membership.assert_called_once_with(
            ctx,
            sample_member.id,
            sample_membership_empty.uuid,
            sample_membership_empty
        )
        
        assert sample_membership_empty.status == MembershipStatus.PENDING_PAYMENT_INITIAL.value
        mock_membership_repository.membership_search_by.assert_called_once()
        mock_member_repository.search_by.assert_called_once()
        mock_member_repository.get_charter.assert_called_once()

    def test_from_pending_rules_to_pending_payment(self, ctx,
                        mock_membership_repository: MagicMock,
                        mock_member_repository: MagicMock,
                        sample_member: Member,
                        sample_membership_duration_no_account: Membership,
                        sample_membership_pending_rules: Membership,
                        member_manager: MemberManager):
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))
        mock_membership_repository.membership_search_by = MagicMock(return_value=([sample_membership_pending_rules], 1))
        mock_member_repository.get_charter = MagicMock(return_value=str(datetime.datetime.today()))
        # When...
        member_manager.change_membership(ctx, sample_member.id, sample_membership_pending_rules.uuid, sample_membership_duration_no_account)

        # Expect to create a new membership record...
        mock_membership_repository.update_membership.assert_called_once_with(
            ctx,
            sample_member.id,
            sample_membership_pending_rules.uuid,
            sample_membership_duration_no_account
        )
        
        assert sample_membership_duration_no_account.status == MembershipStatus.PENDING_PAYMENT.value
        mock_membership_repository.membership_search_by.assert_called_once()
        mock_member_repository.search_by.assert_called_once()
        mock_member_repository.get_charter.assert_called_once()

    def test_from_pending_rules_to_pending_payment_validation(self, ctx,
                        mock_membership_repository: MagicMock,
                        mock_member_repository: MagicMock,
                        mock_account_repository: MagicMock,
                        mock_payment_method_repository: MagicMock,
                        sample_member: Member,
                        sample_membership_pending_rules: Membership,
                        sample_membership_duration_account_payment_method: Membership,
                        sample_account1: Account,
                        sample_payment_method: PaymentMethod,
                        member_manager: MemberManager):
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))
        mock_membership_repository.membership_search_by = MagicMock(return_value=([sample_membership_pending_rules], 1))
        mock_account_repository.search_by = MagicMock(return_value=([sample_account1], 1))
        mock_member_repository.get_charter = MagicMock(return_value=str(datetime.datetime.today()))
        mock_payment_method_repository.search_by = MagicMock(return_value=([sample_payment_method], 1))
        # When...
        member_manager.change_membership(ctx, sample_member.id, sample_membership_pending_rules.uuid, sample_membership_duration_account_payment_method)

        # Expect to create a new membership record...
        mock_membership_repository.update_membership.assert_called_once_with(
            ctx,
            sample_member.id,
            sample_membership_pending_rules.uuid,
            sample_membership_duration_account_payment_method
        )
        
        assert sample_membership_duration_account_payment_method.status == MembershipStatus.PENDING_PAYMENT_VALIDATION.value
        mock_membership_repository.membership_search_by.assert_called_once()
        mock_member_repository.search_by.assert_called_once()
        mock_member_repository.get_charter.assert_called_once()
        mock_account_repository.search_by.assert_called_once()
        mock_payment_method_repository.search_by.assert_called_once()

    def test_from_pending_payment_initial_to_pending_payment(self, ctx,
                        mock_membership_repository: MagicMock,
                        mock_member_repository: MagicMock,
                        sample_member: Member,
                        sample_membership_pending_payment_initial: Membership,
                        sample_membership_duration_no_account: Membership,
                        member_manager: MemberManager):
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))
        mock_membership_repository.membership_search_by = MagicMock(return_value=([sample_membership_pending_payment_initial], 1))
        mock_member_repository.get_charter = MagicMock(return_value=str(datetime.datetime.today()))
        # When...
        member_manager.change_membership(ctx, sample_member.id, sample_membership_pending_payment_initial.uuid, sample_membership_duration_no_account)

        # Expect to create a new membership record...
        mock_membership_repository.update_membership.assert_called_once_with(
            ctx,
            sample_member.id,
            sample_membership_duration_no_account.uuid,
            sample_membership_duration_no_account
        )
        
        assert sample_membership_duration_no_account.status == MembershipStatus.PENDING_PAYMENT.value
        mock_membership_repository.membership_search_by.assert_called_once()
        mock_member_repository.search_by.assert_called_once()
        mock_member_repository.get_charter.assert_not_called()

    def test_from_pending_payment_initial_to_pending_payment_validation(self, ctx,
                        mock_membership_repository: MagicMock,
                        mock_member_repository: MagicMock,
                        mock_account_repository: MagicMock,
                        mock_payment_method_repository: MagicMock,
                        sample_member: Member,
                        sample_membership_pending_payment_initial: Membership,
                        sample_membership_duration_account_payment_method: Membership,
                        sample_account1: Account,
                        sample_payment_method: PaymentMethod,
                        member_manager: MemberManager):
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))
        mock_membership_repository.membership_search_by = MagicMock(return_value=([sample_membership_pending_payment_initial], 0))
        mock_account_repository.search_by = MagicMock(return_value=([sample_account1], 1))
        mock_payment_method_repository.search_by = MagicMock(return_value=([sample_payment_method], 1))
        # When...
        member_manager.change_membership(ctx, sample_member.id, sample_membership_pending_payment_initial.uuid, sample_membership_duration_account_payment_method)

        # Expect to create a new membership record...
        mock_membership_repository.update_membership.assert_called_once_with(
            ctx,
            sample_member.id,
            sample_membership_pending_payment_initial.uuid,
            sample_membership_duration_account_payment_method
        )
        
        assert sample_membership_duration_account_payment_method.status == MembershipStatus.PENDING_PAYMENT_VALIDATION.value
        mock_membership_repository.membership_search_by.assert_called_once()
        mock_member_repository.search_by.assert_called_once()
        mock_account_repository.search_by.assert_called_once()
        mock_member_repository.get_charter.assert_not_called()

    def test_from_pending_payment_to_pending_payment_validation(self, ctx,
                        mock_membership_repository: MagicMock,
                        mock_member_repository: MagicMock,
                        mock_account_repository: MagicMock,
                        mock_payment_method_repository: MagicMock,
                        sample_member: Member,
                        sample_membership_pending_payment: Membership,
                        sample_membership_duration_account_payment_method: Membership,
                        sample_account1: Account,
                        sample_payment_method: PaymentMethod,
                        member_manager: MemberManager):
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))
        mock_membership_repository.membership_search_by = MagicMock(return_value=([sample_membership_pending_payment], 0))
        mock_account_repository.search_by = MagicMock(return_value=([sample_account1], 1))
        mock_payment_method_repository.search_by = MagicMock(return_value=([sample_payment_method], 1))
        # When...
        member_manager.change_membership(ctx, sample_member.id, sample_membership_pending_payment.uuid, sample_membership_duration_account_payment_method)

        # Expect to create a new membership record...
        mock_membership_repository.update_membership.assert_called_once_with(
            ctx,
            sample_member.id,
            sample_membership_pending_payment.uuid,
            sample_membership_duration_account_payment_method
        )
        
        assert sample_membership_duration_account_payment_method.status == MembershipStatus.PENDING_PAYMENT_VALIDATION.value
        mock_membership_repository.membership_search_by.assert_called_once()
        mock_member_repository.search_by.assert_called_once()
        mock_account_repository.search_by.assert_called_once()
        mock_member_repository.get_charter.assert_not_called()

    def test_no_abstract_membership(self, ctx, 
                        mock_membership_repository: MagicMock,
                        mock_member_repository: MagicMock, 
                        sample_member: Member, 
                        sample_membership_pending_rules: Membership, 
                        member_manager: MemberManager):
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))
        mock_membership_repository.membership_search_by = MagicMock(return_value=([sample_membership_pending_rules], 1))

        member_manager.change_membership(ctx, sample_member.id, sample_membership_pending_rules.uuid, None)
        mock_membership_repository.membership_search_by.assert_called_once()
        mock_member_repository.search_by.assert_called_once()
        mock_membership_repository.update_membership.assert_not_called()

    def test_unknown_member(self, ctx,
                        mock_membership_repository: MagicMock, 
                        mock_member_repository: MagicMock,
                        sample_membership_pending_rules: Membership,
                        sample_member: Member,
                        member_manager: MemberManager):
        mock_member_repository.search_by = MagicMock(return_value=([], 0))

        with raises(MemberNotFoundError):
            member_manager.change_membership(ctx, sample_member.id, sample_membership_pending_rules.uuid, None)
            mock_member_repository.search_by.assert_called_once()
            mock_membership_repository.update_membership.assert_not_called()

    def test_unknown_membership(self, ctx,
                        mock_membership_repository: MagicMock, 
                        mock_member_repository: MagicMock,
                        sample_membership_pending_rules: Membership,
                        sample_member: Member,
                        member_manager: MemberManager):
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))
        mock_membership_repository.membership_search_by = MagicMock(return_value=([], 0))

        with raises(MembershipNotFoundError):
            member_manager.change_membership(ctx, sample_member.id, sample_membership_pending_rules.uuid, None)
            mock_membership_repository.update_membership.assert_not_called()

    def test_unknown_account(self, ctx,
                        mock_membership_repository: MagicMock,
                        mock_member_repository: MagicMock,
                        mock_account_repository: MagicMock,
                        sample_member: Member,
                        sample_membership_duration_account_payment_method: Membership,
                        sample_membership_pending_rules: Membership,
                        member_manager: MemberManager):
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))
        mock_membership_repository.membership_search_by = MagicMock(return_value=([sample_membership_pending_rules], 1))
        mock_account_repository.search_by = MagicMock(return_value=([], 0))
        mock_member_repository.get_charter = MagicMock(return_value=str(datetime.datetime.today()))

        with raises(AccountNotFoundError):
            member_manager.change_membership(ctx, sample_member.id, sample_membership_pending_rules.uuid, sample_membership_duration_account_payment_method)
            mock_membership_repository.membership_search_by.assert_called_once()
            mock_member_repository.search_by.assert_called_once()
            mock_account_repository.search_by.assert_called_once()
            mock_member_repository.get_charter.assert_called_once()
            mock_membership_repository.update_membership.assert_not_called()

    def test_unknown_payment_method(self, ctx,
                        mock_membership_repository: MagicMock,
                        mock_member_repository: MagicMock,
                        mock_account_repository: MagicMock,
                        mock_payment_method_repository: MagicMock,
                        sample_member: Member,
                        sample_membership_duration_account_payment_method: Membership,
                        sample_membership_pending_rules: Membership,
                        sample_account1: Account,
                        member_manager: MemberManager):
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))
        mock_membership_repository.membership_search_by = MagicMock(return_value=([sample_membership_pending_rules], 1))
        mock_account_repository.search_by = MagicMock(return_value=([sample_account1], 1))
        mock_member_repository.get_charter = MagicMock(return_value=str(datetime.datetime.today()))
        mock_payment_method_repository.search_by = MagicMock(return_value=([], 0))

        with raises(PaymentMethodNotFoundError):
            member_manager.change_membership(ctx, sample_member.id, sample_membership_pending_rules.uuid, sample_membership_duration_account_payment_method)
            mock_membership_repository.membership_search_by.assert_called_once()
            mock_member_repository.search_by.assert_called_once()
            mock_account_repository.search_by.assert_called_once()
            mock_member_repository.get_charter.assert_called_once()
            mock_payment_method_repository.search_by.assert_called_once()
            mock_membership_repository.update_membership.assert_not_called()

    def test_unknown_price_asign_to_duration(self, ctx,
                        mock_membership_repository: MagicMock,
                        mock_member_repository: MagicMock,
                        mock_account_repository: MagicMock,
                        mock_payment_method_repository: MagicMock,
                        sample_member: Member,
                        sample_membership_duration_account_payment_method: Membership,
                        sample_membership_pending_rules: Membership,
                        sample_account1: Account,
                        member_manager: MemberManager):
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))
        mock_membership_repository.membership_search_by = MagicMock(return_value=([sample_membership_pending_rules], 1))
        mock_account_repository.search_by = MagicMock(return_value=([sample_account1], 1))
        mock_member_repository.get_charter = MagicMock(return_value=str(datetime.datetime.today()))
        mock_payment_method_repository.search_by = MagicMock(return_value=([], 0))
        sample_membership_duration_account_payment_method.duration = 12

        with raises(NoPriceAssignedToThatDuration):
            member_manager.change_membership(ctx, sample_member.id, sample_membership_pending_rules.uuid, sample_membership_duration_account_payment_method)
            mock_membership_repository.membership_search_by.assert_called_once()
            mock_member_repository.search_by.assert_called_once()
            mock_account_repository.search_by.assert_called_once()
            mock_member_repository.get_charter.assert_called_once()
            mock_payment_method_repository.search_by.assert_called_once()
            mock_membership_repository.update_membership.assert_not_called()


class TestValidateMembership:
    def test_unknown_member(self, ctx,
                        mock_membership_repository: MagicMock, 
                        mock_member_repository: MagicMock,
                        sample_membership_empty: Membership,
                        sample_member: Member,
                        member_manager: MemberManager):
        mock_member_repository.search_by = MagicMock(return_value=([], 0))

        with raises(MemberNotFoundError):
            member_manager.validate_membership(ctx, sample_member.id, sample_membership_empty.uuid)
            mock_member_repository.search_by.assert_called_once()
            mock_member_repository.search_by.assert_not_called()
            mock_membership_repository.validate_membership.assert_not_called()

    def test_unknown_membership(self, ctx,
                        mock_membership_repository: MagicMock, 
                        mock_member_repository: MagicMock,
                        sample_member: Member,
                        member_manager: MemberManager):
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))
        mock_membership_repository.membership_search_by = MagicMock(return_value=([], 0))

        with raises(MembershipNotFoundError):
            member_manager.validate_membership(ctx, sample_member.id, "")
            mock_member_repository.search_by.assert_called_once()
            mock_member_repository.search_by.assert_called_once()
            mock_membership_repository.validate_membership.assert_not_called()

    def test_not_payment_validation(self, ctx,
                        mock_membership_repository: MagicMock,
                        mock_member_repository: MagicMock,
                        sample_member: Member,
                        sample_membership_pending_payment: Membership,
                        member_manager: MemberManager):
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))
        mock_membership_repository.membership_search_by = MagicMock(return_value=([sample_membership_pending_payment], 1))

        with raises(MembershipStatusNotAllowed):
            member_manager.validate_membership(ctx, sample_member.id, sample_membership_pending_payment.uuid)
            mock_membership_repository.membership_search_by.assert_called_once()
            mock_member_repository.search_by.assert_called_once()
            mock_membership_repository.validate_membership.assert_not_called()


class TestGetByID:
    def test_happy_path(self, ctx,
                        mock_member_repository: MagicMock,
                        sample_member: Member,
                        member_manager: MemberManager):
        # Given...
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))

        # When...
        result = member_manager.get_by_id(ctx, id=sample_member.id)

        # Expect...
        assert sample_member == result
        mock_member_repository.search_by.assert_called_once_with(ctx, filter_=AbstractMember(id=sample_member.id),
                                                                 limit=DEFAULT_LIMIT,
                                                                 offset=DEFAULT_OFFSET,
                                                                 terms=None)

    def test_not_found(self, ctx,
                       sample_member,
                       mock_member_repository: MagicMock,
                       member_manager: MemberManager):
        # Given...
        mock_member_repository.search_by = MagicMock(return_value=([], 0))

        # When...
        with raises(MemberNotFoundError):
            member_manager.get_by_id(ctx, id=sample_member.id)

        # Expect...
        mock_member_repository.search_by.assert_called_once_with(ctx, filter_=AbstractMember(id=sample_member.id),
                                                                 limit=DEFAULT_LIMIT,
                                                                 offset=DEFAULT_OFFSET,
                                                                 terms=None)


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
                               sample_mutation_request: AbstractMember,
                               member_manager: MemberManager):
        # Given that there is not user in the DB (user will be created).
        mock_member_repository.search_by = MagicMock(return_value=([], 0))

        # When...
        member_manager.update_or_create(ctx, sample_mutation_request)

        # Expect...
        mock_member_repository.create.assert_called_once_with(ctx, sample_mutation_request)

    def test_update_happy_path(self, ctx,
                               mock_member_repository: MagicMock,
                               sample_mutation_request: AbstractMember,
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
        member_manager.update_or_create(ctx, req, id=sample_member.id)

        # Expect...
        mock_member_repository.update.assert_called_once_with(ctx, req, override=True)
        mock_member_repository.create.assert_not_called()  # Do not create any member!


class TestUpdatePartially:
    def test_happy_path(self, ctx,
                        mock_member_repository: MagicMock,
                        sample_member,
                        member_manager: MemberManager):
        updated_comment = 'Updated comment.'
        req = AbstractMember(comment=updated_comment)

        # When...
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))
        member_manager.partially_update(ctx, req, id=sample_member.id)

        # Expect...
        mock_member_repository.update.assert_called_once_with(ctx, req, override=False)

    def test_not_found(self, ctx,
                       mock_member_repository: MagicMock,
                       sample_member,
                       member_manager: MemberManager):
        mock_member_repository.search_by = MagicMock(return_value=([], 0))
        mock_member_repository.update = MagicMock(side_effect=MemberNotFoundError)

        # When...
        with raises(MemberNotFoundError):
            member_manager.partially_update(ctx, AbstractMember(id=sample_member.id), id=sample_member.id)


class TestDelete:
    def test_happy_path(self, ctx,
                        mock_member_repository: MagicMock,
                        sample_member,
                        member_manager: MemberManager):
        # When...
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))
        member_manager.delete(ctx, id=sample_member.id)

        # Expect...
        mock_member_repository.delete.assert_called_once_with(ctx, sample_member.id)

    def test_not_found(self, ctx,
                       mock_member_repository: MagicMock,
                       sample_member,
                       member_manager: MemberManager):
        # Given...
        mock_member_repository.search_by = MagicMock(return_value=([], 0))
        mock_member_repository.delete = MagicMock(side_effect=MemberNotFoundError)

        # When...
        with raises(MemberNotFoundError):
            member_manager.delete(ctx, id=sample_member.id)


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
        result = member_manager.get_logs(ctx, sample_member.id)

        # Expect...
        assert [FAKE_LOGS] == result
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
        username=faker.user_name(),
        email=faker.email(),
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        departure_date=faker.date_this_year(after_today=True).isoformat(),
        comment=faker.sentence(),
        association_mode=faker.date_time_this_year(after_now=True).isoformat(),
        room=sample_room,
    )


@fixture
def member_manager(
        mock_member_repository,
        mock_account_repository,
        mock_account_type_repository,
        mock_payment_method_repository,
        mock_transaction_repository,
        mock_membership_repository,
        mock_logs_repository,
        mock_device_repository,
        device_manager,
):
    return MemberManager(
        member_repository=mock_member_repository,
        account_repository=mock_account_repository,
        account_type_repository=mock_account_type_repository,
        payment_method_repository=mock_payment_method_repository,
        transaction_repository=mock_transaction_repository,
        membership_repository=mock_membership_repository,
        logs_repository=mock_logs_repository,
        device_repository=mock_device_repository,
        device_manager=device_manager,
    )


@fixture
def mock_account_repository():
    return MagicMock(spec=AccountRepository)


@fixture
def mock_account_type_repository():
    return MagicMock(spec=AccountTypeRepository)


@fixture
def mock_transaction_repository():
    return MagicMock(spec=TransactionRepository)


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
def mock_logs_repository():
    r = MagicMock(spec=LogsRepository)
    r.get_logs = MagicMock(return_value=[FAKE_LOGS_OBJ])
    return r


@fixture
def mock_device_repository():
    return MagicMock(spec=DeviceRepository)

@fixture
def sample_membership_pending_rules(sample_member):
    return Membership(
        uuid="",
        member=sample_member,
        status=MembershipStatus.PENDING_RULES.value
    )
    
@fixture
def mock_ip_allocator():
    return MagicMock(spec=IpAllocator)

@fixture
def device_manager(
        mock_device_repository: DeviceRepository,
):
    return DeviceManager(
        device_repository=mock_device_repository,
        ip_allocator=mock_ip_allocator
    )

@fixture
def sample_membership_pending_payment_initial(sample_member):
    return Membership(
        uuid="",
        member=sample_member,
        status=MembershipStatus.PENDING_PAYMENT_INITIAL.value
    )

@fixture
def sample_membership_pending_payment(sample_member):
    return Membership(
        uuid="",
        member=sample_member,
        status=MembershipStatus.PENDING_PAYMENT.value,
        duration=1
    )

@fixture
def sample_membership_pending_payment_validation(sample_member, sample_account1, sample_payment_method):
    return Membership(
        uuid="",
        member=sample_member,
        status=MembershipStatus.PENDING_PAYMENT_VALIDATION.value,
        duration=1,
        account=sample_account1.id,
        payment_method=sample_payment_method.id
    )
