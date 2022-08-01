# coding=utf-8 import datetime import datetime import datetime
import datetime

import pytest
from unittest.mock import MagicMock

from pytest import fixture, raises

from adh6.constants import CTX_ADMIN, CTX_ROLES, MembershipDuration, MembershipStatus
from adh6.entity import AbstractMember, Member, Membership, Account, PaymentMethod
from adh6.entity.member_body import MemberBody
from adh6.entity.subscription_body import SubscriptionBody
from adh6.exceptions import AccountNotFoundError, AccountTypeNotFoundError, LogFetchError, MemberAlreadyExist, MembershipNotFoundError, MembershipStatusNotAllowed, MemberNotFoundError, IntMustBePositive, NoPriceAssignedToThatDuration, PaymentMethodNotFoundError, UnauthorizedError
from adh6.device.interfaces.device_repository import DeviceRepository
from adh6.device.device_manager import DeviceManager
from adh6.device.interfaces.ip_allocator import IpAllocator
from adh6.member.interfaces.logs_repository import LogsRepository
from adh6.member.interfaces.member_repository import MemberRepository
from adh6.member.interfaces.membership_repository import MembershipRepository
from adh6.member.member_manager import MemberManager
from adh6.treasury.interfaces.payment_method_repository import PaymentMethodRepository
from adh6.treasury.interfaces.transaction_repository import TransactionRepository
from adh6.treasury.interfaces.account_type_repository import AccountTypeRepository
from adh6.treasury.interfaces.account_repository import AccountRepository
from adh6.room.interfaces.room_repository import RoomRepository
from adh6.subnet.interfaces.vlan_repository import VlanRepository

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


class TestNewMembership:
    """Unit tests for the management of the memberships
    """
    def test_member_not_found(self, ctx,
                        mock_member_repository: MemberRepository,
                        sample_member: Member,
                        member_manager: MemberManager):
        mock_member_repository.get_by_id = MagicMock(return_value=(None), side_effect=MemberNotFoundError(""))
        # When...
        with pytest.raises(MemberNotFoundError):
            member_manager.create_subscription(ctx, sample_member.id, SubscriptionBody())

    def test_pending_rules(self, ctx,
                        mock_membership_repository: MembershipRepository,
                        mock_member_repository: MemberRepository,
                        sample_member: Member,
                        sample_subscription_empty: SubscriptionBody,
                        member_manager: MemberManager):
        mock_member_repository.get_by_id = MagicMock(return_value=(sample_member))
        mock_membership_repository.search = MagicMock(return_value=([], 0))
        mock_member_repository.get_charter = MagicMock(return_value="")
        # When...
        member_manager.create_subscription(ctx, sample_member.id, sample_subscription_empty)

        # Expect to create a new membership record...
        mock_membership_repository.create.assert_called_once()
    
    def test_pending_payment_initial(self, ctx,
                        mock_membership_repository: MembershipRepository,
                        mock_member_repository: MemberRepository,
                        sample_member: Member,
                        sample_subscription_empty: SubscriptionBody,
                        member_manager: MemberManager):
        mock_member_repository.get_by_id = MagicMock(return_value=(sample_member))
        mock_membership_repository.search = MagicMock(return_value=([], 0))
        mock_member_repository.get_charter = MagicMock(return_value=str(datetime.datetime.today()))
        # When...
        member_manager.create_subscription(ctx, sample_member.id, SubscriptionBody())

        # Expect to create a new membership record...
        mock_membership_repository.create.assert_called_once()

    def test_pending_payment(self, ctx,
                        mock_membership_repository: MembershipRepository,
                        mock_member_repository: MemberRepository,
                        sample_member: Member,
                        sample_subscription_duration_no_account: SubscriptionBody,
                        member_manager: MemberManager):
        mock_member_repository.get_by_id = MagicMock(return_value=(sample_member))
        mock_membership_repository.search = MagicMock(return_value=([], 0))
        mock_member_repository.get_charter = MagicMock(return_value=str(datetime.datetime.today()))
        # When...
        member_manager.create_subscription(ctx, sample_member.id, SubscriptionBody(duration=1))

        # Expect to create a new membership record...
        mock_membership_repository.create.assert_called_once()

    def test_payment_validation(self, ctx,
                        mock_membership_repository: MembershipRepository,
                        mock_member_repository: MemberRepository,
                        mock_account_repository: AccountRepository,
                        mock_payment_method_repository: PaymentMethodRepository,
                        sample_member: Member,
                        sample_subscription_duration_account_payment_method: SubscriptionBody,
                        sample_account1: Account,
                        sample_payment_method: PaymentMethod,
                        member_manager: MemberManager):
        mock_member_repository.get_by_id = MagicMock(return_value=(sample_member))
        mock_membership_repository.search = MagicMock(return_value=([], 0))
        mock_account_repository.get_by_id = MagicMock(return_value=(sample_account1))
        mock_payment_method_repository.get_by_id = MagicMock(return_value=(sample_payment_method))
        mock_member_repository.get_charter = MagicMock(return_value=str(datetime.datetime.today()))
        # When...
        member_manager.create_subscription(ctx, sample_member.id, sample_subscription_duration_account_payment_method)

        # Expect to create a new membership record...
        mock_membership_repository.create.assert_called_once()

    def test_unknown_member(self, ctx,
                        mock_member_repository: MemberRepository,
                        sample_subscription_empty: SubscriptionBody,
                        sample_member: Member,
                        member_manager: MemberManager):
        mock_member_repository.get_by_id = MagicMock(return_value=(sample_member), side_effect=MemberNotFoundError(""))

        with raises(MemberNotFoundError):
            member_manager.create_subscription(ctx, sample_member.id, sample_subscription_empty)

    def test_unknown_account(self, ctx,
                        mock_membership_repository: MembershipRepository,
                        mock_member_repository: MemberRepository,
                        mock_account_repository: AccountRepository,
                        sample_member: Member,
                        sample_subscription_duration_account_payment_method: SubscriptionBody,
                        member_manager: MemberManager):
        mock_member_repository.get_by_id = MagicMock(return_value=(sample_member))
        mock_membership_repository.search = MagicMock(return_value=([], 0))
        mock_account_repository.get_by_id = MagicMock(return_value=(None), side_effect=AccountNotFoundError(""))
        mock_member_repository.get_charter = MagicMock(return_value=str(datetime.datetime.today()))

        with raises(AccountNotFoundError):
            member_manager.create_subscription(ctx, sample_member.id, sample_subscription_duration_account_payment_method)

    def test_unknown_payment_method(self, ctx,
                        mock_membership_repository: MembershipRepository,
                        mock_member_repository: MemberRepository,
                        mock_account_repository: AccountRepository,
                        mock_payment_method_repository: PaymentMethodRepository,
                        sample_member: Member,
                        sample_subscription_duration_account_payment_method: SubscriptionBody,
                        sample_account1: Account,
                        member_manager: MemberManager):
        mock_member_repository.get_by_id = MagicMock(return_value=(sample_member))
        mock_membership_repository.search = MagicMock(return_value=([], 0))
        mock_account_repository.get_by_id = MagicMock(return_value=(sample_account1))
        mock_payment_method_repository.get_by_id = MagicMock(return_value=(None), side_effect=PaymentMethodNotFoundError(""))
        mock_member_repository.get_charter = MagicMock(return_value=str(datetime.datetime.today()))

        with raises(PaymentMethodNotFoundError):
            member_manager.create_subscription(ctx, sample_member.id, sample_subscription_duration_account_payment_method)

    def test_unknown_price_asign_to_duration(self, ctx,
                        mock_membership_repository: MembershipRepository,
                        mock_member_repository: MemberRepository,
                        sample_member: Member,
                        sample_subscription_empty: SubscriptionBody,
                        member_manager: MemberManager):
        mock_member_repository.get_by_id = MagicMock(return_value=(sample_member))
        mock_membership_repository.search = MagicMock(return_value=([], 0))
        mock_member_repository.get_charter = MagicMock(return_value=str(datetime.datetime.today()))
        sample_subscription_empty.duration = 5

        with raises(NoPriceAssignedToThatDuration):
            member_manager.create_subscription(ctx, sample_member.id, sample_subscription_empty)


class TestPatchMembership:
    def test_from_pending_rules_to_pending_payment_initial(self, ctx,
                        mock_membership_repository: MembershipRepository,
                        mock_member_repository: MemberRepository,
                        sample_member: Member,
                        sample_membership_pending_rules: Membership,
                        sample_subscription_empty: SubscriptionBody,
                        member_manager: MemberManager):
        mock_member_repository.get_by_id = MagicMock(return_value=(sample_member))
        mock_membership_repository.search = MagicMock(return_value=([sample_membership_pending_rules], 1))
        mock_member_repository.get_charter = MagicMock(return_value=str(datetime.datetime.today()))
        # When...
        member_manager.update_subscription(ctx, sample_member.id, sample_subscription_empty)

        # Expect to create a new membership record...
        mock_membership_repository.update.assert_called_once()
        
        mock_membership_repository.search.assert_called_once()
        mock_member_repository.get_by_id.assert_called_once()
        mock_member_repository.get_charter.assert_called_once()

    def test_from_pending_rules_to_pending_payment(self, ctx,
                        mock_membership_repository: MembershipRepository,
                        mock_member_repository: MemberRepository,
                        sample_member: Member,
                        sample_subscription_duration_no_account: SubscriptionBody,
                        sample_membership_pending_rules: Membership,
                        member_manager: MemberManager):
        mock_member_repository.get_by_id = MagicMock(return_value=(sample_member))
        mock_membership_repository.search = MagicMock(return_value=([sample_membership_pending_rules], 1))
        mock_member_repository.get_charter = MagicMock(return_value=str(datetime.datetime.today()))
        # When...
        member_manager.update_subscription(ctx, sample_member.id, sample_subscription_duration_no_account)

        # Expect to create a new membership record...
        mock_membership_repository.update.assert_called_once()
        
        mock_membership_repository.search.assert_called_once()
        mock_member_repository.get_by_id.assert_called_once()
        mock_member_repository.get_charter.assert_called_once()

    def test_from_pending_rules_to_pending_payment_validation(self, ctx,
                        mock_membership_repository: MembershipRepository,
                        mock_member_repository: MemberRepository,
                        mock_account_repository: AccountRepository,
                        mock_payment_method_repository: PaymentMethodRepository,
                        sample_member: Member,
                        sample_membership_pending_rules: Membership,
                        sample_subscription_duration_account_payment_method: SubscriptionBody,
                        sample_account1: Account,
                        sample_payment_method: PaymentMethod,
                        member_manager: MemberManager):
        mock_member_repository.get_by_id = MagicMock(return_value=(sample_member))
        mock_membership_repository.search = MagicMock(return_value=([sample_membership_pending_rules], 1))
        mock_account_repository.get_by_id = MagicMock(return_value=(sample_account1))
        mock_member_repository.get_charter = MagicMock(return_value=str(datetime.datetime.today()))
        mock_payment_method_repository.get_by_id = MagicMock(return_value=(sample_payment_method))
        # When...
        member_manager.update_subscription(ctx, sample_member.id, sample_subscription_duration_account_payment_method)

        # Expect to create a new membership record...
        mock_membership_repository.update.assert_called_once()
        
        mock_membership_repository.search.assert_called_once()
        mock_member_repository.get_by_id.assert_called_once()
        mock_member_repository.get_charter.assert_called_once()
        mock_account_repository.get_by_id.assert_called_once()
        mock_payment_method_repository.get_by_id.assert_called_once()

    def test_from_pending_payment_initial_to_pending_payment(self, ctx,
                        mock_membership_repository: MembershipRepository,
                        mock_member_repository: MemberRepository,
                        sample_member: Member,
                        sample_membership_pending_payment_initial: Membership,
                        sample_subscription_duration_no_account: SubscriptionBody,
                        member_manager: MemberManager):
        mock_member_repository.get_by_id = MagicMock(return_value=(sample_member))
        mock_membership_repository.search = MagicMock(return_value=([sample_membership_pending_payment_initial], 1))
        mock_member_repository.get_charter = MagicMock(return_value=str(datetime.datetime.today()))
        # When...
        member_manager.update_subscription(ctx, sample_member.id, sample_subscription_duration_no_account)

        # Expect to create a new membership record...
        mock_membership_repository.update.assert_called_once()
        
        mock_membership_repository.search.assert_called_once()
        mock_member_repository.get_by_id.assert_called_once()
        mock_member_repository.get_charter.assert_not_called()

    def test_from_pending_payment_initial_to_pending_payment_validation(self, ctx,
                        mock_membership_repository: MembershipRepository,
                        mock_member_repository: MemberRepository,
                        mock_account_repository: AccountRepository,
                        mock_payment_method_repository: PaymentMethodRepository,
                        sample_member: Member,
                        sample_membership_pending_payment_initial: Membership,
                        sample_subscription_duration_account_payment_method: SubscriptionBody,
                        sample_account1: Account,
                        sample_payment_method: PaymentMethod,
                        member_manager: MemberManager):
        mock_member_repository.get_by_id = MagicMock(return_value=(sample_member))
        mock_membership_repository.search = MagicMock(return_value=([sample_membership_pending_payment_initial], 1))
        mock_account_repository.get_by_id = MagicMock(return_value=(sample_account1))
        mock_payment_method_repository.get_by_id = MagicMock(return_value=(sample_payment_method))
        # When...
        member_manager.update_subscription(ctx, sample_member.id, sample_subscription_duration_account_payment_method)

        # Expect to create a new membership record...
        mock_membership_repository.update.assert_called_once()
        mock_membership_repository.search.assert_called_once()
        mock_member_repository.get_by_id.assert_called_once()
        mock_account_repository.get_by_id.assert_called_once()
        mock_member_repository.get_charter.assert_not_called()

    def test_from_pending_payment_to_pending_payment_validation(self, ctx,
                        mock_membership_repository: MembershipRepository,
                        mock_member_repository: MemberRepository,
                        mock_account_repository: AccountRepository,
                        mock_payment_method_repository: PaymentMethodRepository,
                        sample_member: Member,
                        sample_membership_pending_payment: Membership,
                        sample_subscription_duration_account_payment_method: SubscriptionBody,
                        sample_account1: Account,
                        sample_payment_method: PaymentMethod,
                        member_manager: MemberManager):
        mock_member_repository.get_by_id = MagicMock(return_value=(sample_member))
        mock_membership_repository.search = MagicMock(return_value=([sample_membership_pending_payment], 1))
        mock_account_repository.get_by_id = MagicMock(return_value=(sample_account1))
        mock_payment_method_repository.get_by_id = MagicMock(return_value=(sample_payment_method))
        # When...
        member_manager.update_subscription(ctx, sample_member.id, sample_subscription_duration_account_payment_method)

        # Expect to create a new membership record...
        mock_membership_repository.update.assert_called_once()
        mock_membership_repository.search.assert_called_once()
        mock_member_repository.get_by_id.assert_called_once()
        mock_account_repository.get_by_id.assert_called_once()
        mock_member_repository.get_charter.assert_not_called()

    def test_unknown_member(self, ctx,
                        mock_membership_repository: MembershipRepository,
                        mock_member_repository: MemberRepository,
                        sample_member: Member,
                        member_manager: MemberManager):
        mock_member_repository.get_by_id = MagicMock(return_value=(sample_member), side_effect=MemberNotFoundError(""))

        with raises(MemberNotFoundError):
            member_manager.update_subscription(ctx, sample_member.id, SubscriptionBody())
            mock_member_repository.get_by_id.assert_called_once()
            mock_membership_repository.update.assert_not_called()

    def test_unknown_membership(self, ctx,
                        mock_membership_repository: MembershipRepository,
                        mock_member_repository: MemberRepository,
                        sample_member: Member,
                        member_manager: MemberManager):
        mock_member_repository.get_by_id = MagicMock(return_value=(sample_member))
        mock_membership_repository.search = MagicMock(return_value=([], 0), side_effect=MembershipNotFoundError(""))

        with raises(MembershipNotFoundError):
            member_manager.update_subscription(ctx, sample_member.id, SubscriptionBody())
            mock_membership_repository.update.assert_not_called()

    def test_unknown_account(self, ctx,
                        mock_membership_repository: MembershipRepository,
                        mock_member_repository: MemberRepository,
                        mock_account_repository: AccountRepository,
                        sample_member: Member,
                        sample_subscription_duration_account_payment_method: SubscriptionBody,
                        sample_membership_pending_rules: Membership,
                        member_manager: MemberManager):
        mock_member_repository.get_by_id = MagicMock(return_value=(sample_member))
        mock_membership_repository.search = MagicMock(return_value=([sample_membership_pending_rules], 1))
        mock_account_repository.get_by_id = MagicMock(return_value=(None), side_effect=AccountNotFoundError(""))
        mock_member_repository.get_charter = MagicMock(return_value=str(datetime.datetime.today()))

        with raises(AccountNotFoundError):
            member_manager.update_subscription(ctx, sample_member.id, sample_subscription_duration_account_payment_method)

        mock_membership_repository.search.assert_called_once()
        mock_member_repository.get_by_id.assert_called_once()
        mock_account_repository.get_by_id.assert_called_once()
        mock_member_repository.get_charter.assert_called_once()
        mock_membership_repository.update.assert_not_called()

    def test_unknown_payment_method(self, ctx,
                        mock_membership_repository: MembershipRepository,
                        mock_member_repository: MemberRepository,
                        mock_account_repository: AccountRepository,
                        mock_payment_method_repository: PaymentMethodRepository,
                        sample_member: Member,
                        sample_subscription_duration_account_payment_method: SubscriptionBody,
                        sample_membership_pending_rules: Membership,
                        sample_account1: Account,
                        member_manager: MemberManager):
        mock_member_repository.get_by_id = MagicMock(return_value=(sample_member))
        mock_membership_repository.search = MagicMock(return_value=([sample_membership_pending_rules], 1))
        mock_account_repository.get_by_id = MagicMock(return_value=(sample_account1))
        mock_member_repository.get_charter = MagicMock(return_value=str(datetime.datetime.today()))
        mock_payment_method_repository.get_by_id = MagicMock(return_value=(None), side_effect=PaymentMethodNotFoundError(""))

        with raises(PaymentMethodNotFoundError):
            member_manager.update_subscription(ctx, sample_member.id, sample_subscription_duration_account_payment_method)

        mock_membership_repository.search.assert_called_once()
        mock_member_repository.get_by_id.assert_called_once()
        mock_account_repository.get_by_id.assert_called_once()
        mock_member_repository.get_charter.assert_called_once()
        mock_payment_method_repository.get_by_id.assert_called_once()
        mock_membership_repository.update.assert_not_called()

    def test_unknown_price_asign_to_duration(self, ctx,
                        mock_membership_repository: MembershipRepository,
                        mock_member_repository: MemberRepository,
                        sample_member: Member,
                        sample_subscription_duration_account_payment_method: SubscriptionBody,
                        sample_membership_pending_rules: Membership,
                        member_manager: MemberManager):
        mock_member_repository.get_by_id = MagicMock(return_value=(sample_member))
        mock_membership_repository.search = MagicMock(return_value=([sample_membership_pending_rules], 1))
        mock_member_repository.get_charter = MagicMock(return_value=str(datetime.datetime.today()))
        sample_subscription_duration_account_payment_method.duration = 5

        with raises(NoPriceAssignedToThatDuration):
            member_manager.update_subscription(ctx, sample_member.id, sample_subscription_duration_account_payment_method)
            
        mock_membership_repository.search.assert_called_once()
        mock_member_repository.get_by_id.assert_called_once()
        mock_member_repository.get_charter.assert_called_once()
        mock_membership_repository.update.assert_not_called()


class TestValidateMembership:
    def test_unknown_member(self, ctx,
                        mock_member_repository: MemberRepository,
                        member_manager: MemberManager):
        mock_member_repository.get_by_id = MagicMock(side_effect=MemberNotFoundError(""))

        with raises(MemberNotFoundError):
            member_manager.validate_subscription(ctx, 0, False)

        mock_member_repository.get_by_id.assert_called_once()

    def test_unknown_membership(self, ctx,
                        mock_membership_repository: MembershipRepository, 
                        mock_member_repository: MemberRepository,
                        sample_member: Member,
                        member_manager: MemberManager):
        mock_member_repository.get_by_id = MagicMock(return_value=(sample_member))
        mock_membership_repository.search = MagicMock(return_value=([], 0))

        with raises(MembershipNotFoundError):
            member_manager.validate_subscription(ctx, sample_member.id, False)

        mock_member_repository.get_by_id.assert_called_once()
        mock_membership_repository.search.assert_called_once()

    def test_not_payment_validation(self, ctx,
                        mock_membership_repository: MembershipRepository,
                        mock_member_repository: MemberRepository,
                        sample_member: Member,
                        sample_membership_pending_payment: Membership,
                        member_manager: MemberManager):
        mock_member_repository.get_by_id = MagicMock(return_value=(sample_member))
        mock_membership_repository.search = MagicMock(return_value=([sample_membership_pending_payment], 1))

        with raises(MembershipStatusNotAllowed):
            member_manager.validate_subscription(ctx, sample_member.id, False)

        mock_membership_repository.search.assert_called_once()
        mock_member_repository.get_by_id.assert_called_once()


class TestAddMembershipPaymentRecord:
    def test_no_asso_account(self, ctx,
                        mock_payment_method_repository: PaymentMethodRepository,
                        mock_account_repository: AccountRepository,
                        member_manager: MemberManager,
                        sample_membership_empty: Membership):
        mock_payment_method_repository.get_by_id = MagicMock(return_value=()) # in this test don't care of the return value, the most important thing is that the function does not raise NotFound exception
        mock_account_repository.search_by = MagicMock(side_effect=[([], 0)])

        with raises(AccountNotFoundError):
            member_manager.add_membership_payment_record(ctx, sample_membership_empty, False)

        mock_payment_method_repository.get_by_id.assert_called_once()
        mock_account_repository.search_by.assert_called_once()

    def test_no_tech_account(self, ctx,
                        mock_payment_method_repository: PaymentMethodRepository,
                        mock_account_repository: AccountRepository,
                        member_manager: MemberManager,
                        sample_membership_empty: Membership,
                        sample_account1: Account,
                        sample_payment_method: PaymentMethod):
        mock_payment_method_repository.get_by_id = MagicMock(return_value=(sample_payment_method)) # in this test don't care of the return value, the most important thing is that the function does not raise NotFound exception
        mock_account_repository.search_by = MagicMock(side_effect=[([sample_account1], 0), ([], 0)])

        with raises(AccountNotFoundError):
            member_manager.add_membership_payment_record(ctx, sample_membership_empty, False)

        mock_payment_method_repository.get_by_id.assert_called_once()
        mock_account_repository.search_by.assert_called()

    def test_no_src_account(self, ctx,
                        mock_payment_method_repository: PaymentMethodRepository,
                        mock_account_repository: AccountRepository,
                        member_manager: MemberManager,
                        sample_membership_empty: Membership,
                        sample_account1: Account,
                        sample_payment_method: PaymentMethod):
        mock_payment_method_repository.get_by_id = MagicMock(return_value=(sample_payment_method)) # in this test don't care of the return value, the most important thing is that the function does not raise NotFound exception
        mock_account_repository.search_by = MagicMock(side_effect=[([sample_account1], 0), ([sample_account1], 0)])
        mock_account_repository.get_by_id = MagicMock(side_effect=AccountNotFoundError(""))

        with raises(AccountNotFoundError):
            member_manager.add_membership_payment_record(ctx, sample_membership_empty, False)

        mock_payment_method_repository.get_by_id.assert_called_once()
        mock_account_repository.search_by.assert_called()
        mock_account_repository.get_by_id.assert_called_once()

    def test_no_room(self, ctx,
                        mock_payment_method_repository: PaymentMethodRepository,
                        mock_account_repository: AccountRepository,
                        mock_transaction_repository: TransactionRepository,
                        member_manager: MemberManager,
                        sample_membership_pending_payment_validation: Membership,
                        sample_account1: Account,
                        sample_payment_method: PaymentMethod):
        mock_payment_method_repository.get_by_id = MagicMock(return_value=(sample_payment_method)) # in this test don't care of the return value, the most important thing is that the function does not raise NotFound exception
        mock_account_repository.search_by = MagicMock(side_effect=[([sample_account1], 0), ([sample_account1], 0)])
        mock_account_repository.get_by_id = MagicMock(return_value=(sample_account1))
        mock_transaction_repository.create = MagicMock(return_value=(None))

        sample_membership_pending_payment_validation.has_room = False

        member_manager.add_membership_payment_record(ctx, sample_membership_pending_payment_validation, False)

        mock_payment_method_repository.get_by_id.assert_called_once()
        mock_account_repository.search_by.assert_called()
        mock_account_repository.get_by_id.assert_called_once()
        mock_transaction_repository.create.assert_called_once()

    def test_free(self, ctx,
                        mock_payment_method_repository: PaymentMethodRepository,
                        mock_account_repository: AccountRepository,
                        mock_transaction_repository: TransactionRepository,
                        member_manager: MemberManager,
                        sample_membership_pending_payment_validation: Membership,
                        sample_account1: Account,
                        sample_payment_method: PaymentMethod):
        mock_payment_method_repository.get_by_id = MagicMock(return_value=(sample_payment_method)) # in this test don't care of the return value, the most important thing is that the function does not raise NotFound exception
        mock_account_repository.search_by = MagicMock(side_effect=[([sample_account1], 0), ([sample_account1], 0)])
        mock_account_repository.get_by_id = MagicMock(return_value=(sample_account1))
        mock_transaction_repository.create = MagicMock(return_value=(None))

        member_manager.add_membership_payment_record(ctx, sample_membership_pending_payment_validation, True)

        mock_payment_method_repository.get_by_id.assert_called_once()
        mock_account_repository.search_by.assert_called()
        mock_account_repository.get_by_id.assert_called_once()
        mock_transaction_repository.create.assert_called_once()

    def test_free_not_super_admin(self, ctx_only_admin, member_manager: MemberManager, sample_membership_pending_payment_validation: Membership):
        with pytest.raises(UnauthorizedError):
            member_manager.add_membership_payment_record(ctx_only_admin, sample_membership_pending_payment_validation, True)


class TestProfile:
    def test_happy_path(self, ctx,
                        mock_member_repository: MemberRepository,
                        sample_member: Member,
                        member_manager: MemberManager):
        # Given...
        mock_member_repository.get_by_id = MagicMock(return_value=(sample_member))

        # When...
        m, roles = member_manager.get_profile(ctx)

        # Expect...
        assert sample_member == m
        assert len(roles) == len(ctx.get(CTX_ROLES))
        assert len(roles) == len(set(roles) & set(ctx.get(CTX_ROLES)))
        mock_member_repository.get_by_id.assert_called_once_with(ctx, ctx.get(CTX_ADMIN))

    def test_member_not_found(self, ctx,
                        mock_member_repository: MemberRepository,
                        member_manager: MemberManager):
        # Given...
        mock_member_repository.get_by_id = MagicMock(return_value=(None), side_effect=MemberNotFoundError(""))

        # When...
        with pytest.raises(MemberNotFoundError):
            member_manager.get_profile(ctx)

        # Expect...
        mock_member_repository.get_by_id.assert_called_once_with(ctx, ctx.get(CTX_ADMIN))


class TestGetByID:
    def test_happy_path(self, ctx,
                        mock_member_repository: MemberRepository,
                        mock_membership_repository: MembershipRepository,
                        sample_member: Member,
                        member_manager: MemberManager):
        # Given...
        mock_member_repository.get_by_id = MagicMock(return_value=(sample_member))
        mock_membership_repository.search = MagicMock(return_value=([], 0))

        # When...
        result = member_manager.get_by_id(ctx, id=sample_member.id)

        # Expect...
        assert sample_member == result
        mock_member_repository.get_by_id.assert_called_once_with(ctx, sample_member.id)

    def test_not_found(self, ctx,
                       sample_member,
                       mock_member_repository: MemberRepository,
                       member_manager: MemberManager):
        # Given...
        mock_member_repository.get_by_id = MagicMock(return_value=(None), side_effect=MemberNotFoundError(""))

        # When...
        with raises(MemberNotFoundError):
            member_manager.get_by_id(ctx, id=sample_member.id)

        # Expect...
        mock_member_repository.get_by_id.assert_called_once_with(ctx, sample_member.id)


class TestSearch:
    def test_happy_path(self, ctx,
                        mock_member_repository: MemberRepository,
                        sample_member: Member,
                        member_manager: MemberManager):
        # Given...
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))

        # When...
        test_terms = 'blah blah blah'
        test_offset = 42
        test_limit = 99
        result, _ = member_manager.search(ctx, limit=test_limit, offset=test_offset, terms=test_terms)

        # Expect...
        assert [sample_member] == result

        # Make sure that all the parameters are passed to the DB.
        mock_member_repository.search_by.assert_called_once_with(ctx,
                                                                 limit=test_limit,
                                                                 offset=test_offset,
                                                                 terms=test_terms)


class TestNewMember:
    def test_member_already_exist(self, ctx,
                        mock_member_repository: MemberRepository,
                        sample_member: AbstractMember,
                        member_manager: MemberManager):
        # Given...
        mock_member_repository.get_by_login = MagicMock(return_value=(sample_member))

        # When...
        with pytest.raises(MemberAlreadyExist):
            member_manager.create(ctx, body=MemberBody(username=sample_member.username))

        # Expect...
        mock_member_repository.get_by_login.assert_called_once_with(ctx, sample_member.username)

    def test_no_account_type_adherent(self, ctx,
                        mock_member_repository: MemberRepository,
                        mock_account_type_repository: AccountTypeRepository,
                        member_manager: MemberManager):
        # Given...
        mock_member_repository.get_by_login = MagicMock(return_value=(None))
        mock_account_type_repository.search_by = MagicMock(return_value=([], 0))

        # When...
        with pytest.raises(AccountTypeNotFoundError):
            member_manager.create(ctx, body=MemberBody(
                                      username="testtest",
                                  ))

        # Expect...
        mock_account_type_repository.search_by.assert_called_once_with(ctx, terms="Adhérent")


class TestCreateOrUpdate:

    def test_create_happy_path(self, ctx,
                               mock_member_repository: MagicMock,
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
                        mock_membership_repository: MembershipRepository,
                        mock_logs_repository: MagicMock,
                        mock_member_repository: MagicMock,
                        mock_device_repository: MagicMock,
                        sample_member: Member,
                        member_manager: MemberManager):
        # Given...
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))
        mock_membership_repository.search = MagicMock(return_value=([], 0))
        mock_logs_repository.get_logs = MagicMock(return_value=([FAKE_LOGS]))

        # When...
        result = member_manager.get_logs(ctx, sample_member.id)

        # Expect...
        assert [FAKE_LOGS] == result
        devices = mock_device_repository.search_by(ctx, username=sample_member.username)
        mock_logs_repository.get_logs.assert_called_once_with(ctx, devices=devices.__getitem__(),
                                                              username=sample_member.username, dhcp=False)

    def test_fetch_failed(self, ctx,
                        mock_membership_repository: MembershipRepository,
                          mock_logs_repository: MagicMock,
                          mock_member_repository: MagicMock,
                          sample_member: Member,
                          member_manager: MemberManager):
        # Given...
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))
        mock_membership_repository.search = MagicMock(return_value=([], 0))
        mock_logs_repository.get_logs = MagicMock(side_effect=LogFetchError)

        # When...
        result = member_manager.get_logs(ctx, sample_member.username)

        # Expect use case to 'fail open', do not throw any error, assume there is no log.
        assert [] == result

    def test_not_found(self, ctx,
                        mock_membership_repository: MembershipRepository,
                       sample_member,
                       member_manager: MemberManager):
        # Given...
        mock_membership_repository.search = MagicMock(side_effect=MemberNotFoundError)

        # When...
        with raises(MemberNotFoundError):
            member_manager.get_logs(ctx, sample_member.username)


@fixture
def sample_mutation_request(faker):
    return AbstractMember(
        username=faker.user_name(),
        email=faker.email(),
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        departure_date=faker.date_this_year(after_today=True).isoformat(),
        comment=faker.sentence(),
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
def device_manager(
        mock_device_repository: DeviceRepository,
        mock_member_repository: MemberRepository,
        mock_ip_allocator: IpAllocator,
        mock_vlan_repository: VlanRepository,
):
    return DeviceManager(
        device_repository=mock_device_repository,
        ip_allocator=mock_ip_allocator,
        member_repository=mock_member_repository,
        vlan_repository=mock_vlan_repository,
    )

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
