import pytest
import datetime

from unittest.mock import MagicMock

from adh6.member import MembershipStatus, MembershipDuration, SubscriptionManager
from adh6.entity import Member, Membership, Account, PaymentMethod, SubscriptionBody
from adh6.exceptions import AccountNotFoundError, MembershipNotFoundError, MembershipStatusNotAllowed, MemberNotFoundError, NoPriceAssignedToThatDuration, PaymentMethodNotFoundError, UnauthorizedError
from adh6.member import CharterManager
from adh6.member.interfaces import MemberRepository, MembershipRepository
from adh6.treasury import TransactionManager, PaymentMethodManager, AccountManager
from adh6.member.notification_manager import NotificationManager


class TestNewMembership:
    """Unit tests for the management of the memberships
    """
    def test_pending_rules(self,
                        mock_subscription_repository: MembershipRepository,
                        sample_member: Member,
                        mock_charter_manager: CharterManager,
                        sample_subscription_empty: SubscriptionBody,
                        subscription_manager: SubscriptionManager):
        mock_subscription_repository.from_member = MagicMock(return_value=([]))
        mock_charter_manager.get = MagicMock(return_value="")
        # When...
        subscription_manager.create(sample_member, sample_subscription_empty)

        # Expect to create a new membership record...
        mock_subscription_repository.create.assert_called_once()
    
    def test_pending_payment_initial(self,
                        mock_subscription_repository: MembershipRepository,
                        sample_member: Member,
                        mock_charter_manager: CharterManager,
                        subscription_manager: SubscriptionManager):
        mock_subscription_repository.from_member = MagicMock(return_value=([]))
        mock_charter_manager.get = MagicMock(return_value=str(datetime.datetime.today()))
        # When...
        subscription_manager.create(sample_member.id, SubscriptionBody())

        # Expect to create a new membership record...
        mock_subscription_repository.create.assert_called_once()

    def test_pending_payment(self,
                        mock_subscription_repository: MembershipRepository,
                        sample_member: Member,
                        mock_charter_manager: CharterManager,
                        subscription_manager: SubscriptionManager):
        mock_subscription_repository.from_member = MagicMock(return_value=([]))
        mock_charter_manager.get = MagicMock(return_value=str(datetime.datetime.today()))
        # When...
        subscription_manager.create(sample_member.id, SubscriptionBody(duration=1))

        # Expect to create a new membership record...
        mock_subscription_repository.create.assert_called_once()

    def test_payment_validation(self,
                        mock_subscription_repository: MembershipRepository,
                        mock_account_manager: AccountManager,
                        mock_payment_method_manager: PaymentMethodManager,
                        sample_member: Member,
                        mock_charter_manager: CharterManager,
                        sample_subscription_duration_account_payment_method: SubscriptionBody,
                        sample_account1: Account,
                        sample_payment_method: PaymentMethod,
                        subscription_manager: SubscriptionManager):
        mock_subscription_repository.from_member = MagicMock(return_value=([]))
        mock_account_manager.get_by_id = MagicMock(return_value=(sample_account1))
        mock_payment_method_manager.get_by_id = MagicMock(return_value=(sample_payment_method))
        mock_charter_manager.get = MagicMock(return_value=str(datetime.datetime.today()))
        # When...
        subscription_manager.create(sample_member.id, sample_subscription_duration_account_payment_method)

        # Expect to create a new membership record...
        mock_subscription_repository.create.assert_called_once()

    def test_unknown_account(self,
                        mock_subscription_repository: MembershipRepository,
                        mock_account_manager: AccountManager,
                        sample_member: Member,
                        mock_charter_manager: CharterManager,
                        sample_subscription_duration_account_payment_method: SubscriptionBody,
                        subscription_manager: SubscriptionManager):
        mock_subscription_repository.from_member = MagicMock(return_value=([]))
        mock_account_manager.get_by_id = MagicMock(return_value=(None), side_effect=AccountNotFoundError(""))
        mock_charter_manager.get = MagicMock(return_value=str(datetime.datetime.today()))

        with pytest.raises(AccountNotFoundError):
            subscription_manager.create(sample_member.id, sample_subscription_duration_account_payment_method)

    def test_unknown_payment_method(self,
                        mock_subscription_repository: MembershipRepository,
                        mock_account_manager: AccountManager,
                        mock_payment_method_manager: PaymentMethodManager,
                        sample_member: Member,
                        mock_charter_manager: CharterManager,
                        sample_subscription_duration_account_payment_method: SubscriptionBody,
                        sample_account1: Account,
                        subscription_manager: SubscriptionManager):
        mock_subscription_repository.from_member = MagicMock(return_value=([]))
        mock_account_manager.get_by_id = MagicMock(return_value=(sample_account1))
        mock_payment_method_manager.get_by_id = MagicMock(return_value=(None), side_effect=PaymentMethodNotFoundError(""))
        mock_charter_manager.get = MagicMock(return_value=str(datetime.datetime.today()))

        with pytest.raises(PaymentMethodNotFoundError):
            subscription_manager.create(sample_member.id, sample_subscription_duration_account_payment_method)

    def test_unknown_price_asign_to_duration(self,
                        mock_subscription_repository: MembershipRepository,
                        sample_member: Member,
                        mock_charter_manager: CharterManager,
                        sample_subscription_empty: SubscriptionBody,
                        subscription_manager: SubscriptionManager):
        mock_subscription_repository.from_member = MagicMock(return_value=([]))
        mock_charter_manager.get = MagicMock(return_value=str(datetime.datetime.today()))
        sample_subscription_empty.duration = 5

        with pytest.raises(NoPriceAssignedToThatDuration):
            subscription_manager.create(sample_member.id, sample_subscription_empty)


class TestPatchMembership:
    def test_from_pending_rules_to_pending_payment_initial(self,
                        mock_subscription_repository: MembershipRepository,
                        sample_member: Member,
                        mock_charter_manager: CharterManager,
                        sample_membership_pending_rules: Membership,
                        sample_subscription_empty: SubscriptionBody,
                        subscription_manager: SubscriptionManager):
        mock_subscription_repository.from_member = MagicMock(return_value=([sample_membership_pending_rules]))
        mock_charter_manager.get = MagicMock(return_value=str(datetime.datetime.today()))
        # When...
        subscription_manager.update(sample_member, sample_subscription_empty)

        # Expect to create a new membership record...
        mock_subscription_repository.update.assert_called_once()
        
        mock_subscription_repository.from_member.assert_called_once()
        mock_charter_manager.get.assert_called_once()

    def test_from_pending_rules_to_pending_payment(self,
                        mock_subscription_repository: MembershipRepository,
                        sample_member: Member,
                        mock_charter_manager: CharterManager,
                        sample_subscription_duration_no_account: SubscriptionBody,
                        sample_membership_pending_rules: Membership,
                        subscription_manager: SubscriptionManager):
        mock_subscription_repository.from_member = MagicMock(return_value=([sample_membership_pending_rules]))
        mock_charter_manager.get = MagicMock(return_value=str(datetime.datetime.today()))
        # When...
        subscription_manager.update(sample_member, sample_subscription_duration_no_account)

        # Expect to create a new membership record...
        mock_subscription_repository.update.assert_called_once()
        
        mock_subscription_repository.from_member.assert_called_once()
        mock_charter_manager.get.assert_called_once()

    def test_from_pending_rules_to_pending_payment_validation(self,
                        mock_subscription_repository: MembershipRepository,
                        mock_account_manager: AccountManager,
                        mock_payment_method_manager: PaymentMethodManager,
                        sample_member: Member,
                        mock_charter_manager: CharterManager,
                        sample_membership_pending_rules: Membership,
                        sample_subscription_duration_account_payment_method: SubscriptionBody,
                        sample_account1: Account,
                        sample_payment_method: PaymentMethod,
                        subscription_manager: SubscriptionManager):
        mock_subscription_repository.from_member = MagicMock(return_value=([sample_membership_pending_rules]))
        mock_account_manager.get_by_id = MagicMock(return_value=(sample_account1))
        mock_charter_manager.get = MagicMock(return_value=str(datetime.datetime.today()))
        mock_payment_method_manager.get_by_id = MagicMock(return_value=(sample_payment_method))
        # When...
        subscription_manager.update(sample_member, sample_subscription_duration_account_payment_method)

        # Expect to create a new membership record...
        mock_subscription_repository.update.assert_called_once()
        
        mock_subscription_repository.from_member.assert_called_once()
        mock_charter_manager.get.assert_called_once()
        mock_account_manager.get_by_id.assert_called_once()
        mock_payment_method_manager.get_by_id.assert_called_once()

    def test_from_pending_payment_initial_to_pending_payment(self,
                        mock_subscription_repository: MembershipRepository,
                        sample_member: Member,
                        mock_charter_manager: CharterManager,
                        sample_membership_pending_payment_initial: Membership,
                        sample_subscription_duration_no_account: SubscriptionBody,
                        subscription_manager: SubscriptionManager):
        mock_subscription_repository.from_member = MagicMock(return_value=([sample_membership_pending_payment_initial]))
        mock_charter_manager.get = MagicMock(return_value=str(datetime.datetime.today()))
        # When...
        subscription_manager.update(sample_member, sample_subscription_duration_no_account)

        # Expect to create a new membership record...
        mock_subscription_repository.update.assert_called_once()
        
        mock_subscription_repository.from_member.assert_called_once()
        mock_charter_manager.get.assert_not_called()

    def test_from_pending_payment_initial_to_pending_payment_validation(self,
                        mock_subscription_repository: MembershipRepository,
                        mock_account_manager: AccountManager,
                        mock_payment_method_manager: PaymentMethodManager,
                        sample_member: Member,
                        sample_membership_pending_payment_initial: Membership,
                        sample_subscription_duration_account_payment_method: SubscriptionBody,
                        sample_account1: Account,
                        sample_payment_method: PaymentMethod,
                        subscription_manager: SubscriptionManager):
        mock_subscription_repository.from_member = MagicMock(return_value=([sample_membership_pending_payment_initial]))
        mock_account_manager.get_by_id = MagicMock(return_value=(sample_account1))
        mock_payment_method_manager.get_by_id = MagicMock(return_value=(sample_payment_method))
        # When...
        subscription_manager.update(sample_member, sample_subscription_duration_account_payment_method)

        # Expect to create a new membership record...
        mock_subscription_repository.update.assert_called_once()
        mock_subscription_repository.from_member.assert_called_once()
        mock_account_manager.get_by_id.assert_called_once()

    def test_from_pending_payment_to_pending_payment_validation(self,
                        mock_subscription_repository: MembershipRepository,
                        mock_member_repository: MemberRepository,
                        mock_account_manager: AccountManager,
                        mock_payment_method_manager: PaymentMethodManager,
                        sample_member: Member,
                        sample_membership_pending_payment: Membership,
                        sample_subscription_duration_account_payment_method: SubscriptionBody,
                        sample_account1: Account,
                        sample_payment_method: PaymentMethod,
                        subscription_manager: SubscriptionManager):
        mock_subscription_repository.from_member = MagicMock(return_value=([sample_membership_pending_payment]))
        mock_account_manager.get_by_id = MagicMock(return_value=(sample_account1))
        mock_payment_method_manager.get_by_id = MagicMock(return_value=(sample_payment_method))
        # When...
        subscription_manager.update(sample_member, sample_subscription_duration_account_payment_method)

        # Expect to create a new membership record...
        mock_subscription_repository.update.assert_called_once()
        mock_subscription_repository.from_member.assert_called_once()
        mock_account_manager.get_by_id.assert_called_once()

    def test_unknown_membership(self,
                        mock_subscription_repository: MembershipRepository,
                        sample_member: Member,
                        subscription_manager: SubscriptionManager):
        mock_subscription_repository.from_member = MagicMock(return_value=([]))

        with pytest.raises(MembershipNotFoundError):
            subscription_manager.update(sample_member, SubscriptionBody())

    def test_unknown_account(self,
                        mock_subscription_repository: MembershipRepository,
                        mock_account_manager: AccountManager,
                        sample_member: Member,
                        mock_charter_manager: CharterManager,
                        sample_subscription_duration_account_payment_method: SubscriptionBody,
                        sample_membership_pending_rules: Membership,
                        subscription_manager: SubscriptionManager):
        mock_subscription_repository.from_member = MagicMock(return_value=([sample_membership_pending_rules]))
        mock_account_manager.get_by_id = MagicMock(return_value=(None), side_effect=AccountNotFoundError(""))
        mock_charter_manager.get = MagicMock(return_value=str(datetime.datetime.today()))

        with pytest.raises(AccountNotFoundError):
            subscription_manager.update(sample_member.id, sample_subscription_duration_account_payment_method)

        mock_subscription_repository.from_member.assert_called_once()
        mock_account_manager.get_by_id.assert_called_once()
        mock_charter_manager.get.assert_called_once()
        mock_subscription_repository.update.assert_not_called()

    def test_unknown_payment_method(self,
                        mock_subscription_repository: MembershipRepository,
                        mock_charter_manager: CharterManager,
                        mock_account_manager: AccountManager,
                        mock_payment_method_manager: PaymentMethodManager,
                        sample_member: Member,
                        sample_subscription_duration_account_payment_method: SubscriptionBody,
                        sample_membership_pending_rules: Membership,
                        sample_account1: Account,
                        subscription_manager: SubscriptionManager):
        mock_subscription_repository.from_member = MagicMock(return_value=([sample_membership_pending_rules]))
        mock_account_manager.get_by_id = MagicMock(return_value=(sample_account1))
        mock_charter_manager.get = MagicMock(return_value=str(datetime.datetime.today()))
        mock_payment_method_manager.get_by_id = MagicMock(return_value=(None), side_effect=PaymentMethodNotFoundError(""))

        with pytest.raises(PaymentMethodNotFoundError):
            subscription_manager.update(sample_member, sample_subscription_duration_account_payment_method)

        mock_subscription_repository.from_member.assert_called_once()
        mock_account_manager.get_by_id.assert_called_once()
        mock_charter_manager.get.assert_called_once()
        mock_payment_method_manager.get_by_id.assert_called_once()
        mock_subscription_repository.update.assert_not_called()

    def test_unknown_price_asign_to_duration(self,
                        mock_subscription_repository: MembershipRepository,
                        mock_charter_manager: CharterManager,
                        sample_member: Member,
                        sample_subscription_duration_account_payment_method: SubscriptionBody,
                        sample_membership_pending_rules: Membership,
                        subscription_manager: SubscriptionManager):
        mock_subscription_repository.from_member = MagicMock(return_value=([sample_membership_pending_rules]))
        mock_charter_manager.get = MagicMock(return_value=str(datetime.datetime.today()))
        sample_subscription_duration_account_payment_method.duration = 5

        with pytest.raises(NoPriceAssignedToThatDuration):
            subscription_manager.update(sample_member.id, sample_subscription_duration_account_payment_method)
            
        mock_subscription_repository.from_member.assert_called()
        mock_charter_manager.get.assert_called_once()
        mock_subscription_repository.update.assert_not_called()


class TestValidateMembership:
    def test_unknown_membership(self,
                        mock_subscription_repository: MembershipRepository, 
                        mock_member_repository: MemberRepository,
                        sample_member: Member,
                        subscription_manager: SubscriptionManager):
        mock_member_repository.get_by_id = MagicMock(return_value=(sample_member))
        mock_subscription_repository.from_member = MagicMock(return_value=([]))

        with pytest.raises(MembershipNotFoundError):
            subscription_manager.validate(sample_member, False)

        mock_member_repository.get_by_id.assert_called()
        mock_subscription_repository.from_member.assert_called_once()

    def test_not_payment_validation(self,
                        mock_subscription_repository: MembershipRepository,
                        mock_member_repository: MemberRepository,
                        sample_member: Member,
                        sample_membership_pending_payment: Membership,
                        subscription_manager: SubscriptionManager):
        mock_member_repository.get_by_id = MagicMock(return_value=(sample_member))
        mock_subscription_repository.from_member = MagicMock(return_value=([sample_membership_pending_payment]))

        with pytest.raises(MembershipStatusNotAllowed):
            subscription_manager.validate(sample_member, False)

        mock_subscription_repository.from_member.assert_called_once()
        mock_member_repository.get_by_id.assert_called()


class TestAddMembershipPaymentRecord:
    def test_no_asso_account(self,
                        mock_payment_method_manager: PaymentMethodManager,
                        mock_account_manager: AccountManager,
                        subscription_manager: SubscriptionManager,
                        sample_membership_empty: Membership):
        mock_payment_method_manager.get_by_id = MagicMock(return_value=()) # in this test don't care of the return value, the most important thing is that the function does not raise NotFound exception
        mock_account_manager.get_by_name = MagicMock(side_effect=AccountNotFoundError(""))

        with pytest.raises(AccountNotFoundError):
            subscription_manager.add_payment_record(sample_membership_empty, False)

        mock_payment_method_manager.get_by_id.assert_called_once()
        mock_account_manager.get_by_name.assert_called_once()

    def test_no_tech_account(self,
                        mock_payment_method_manager: PaymentMethodManager,
                        mock_account_manager: AccountManager,
                        subscription_manager: SubscriptionManager,
                        sample_membership_empty: Membership,
                        sample_account1: Account,
                        sample_payment_method: PaymentMethod):
        mock_payment_method_manager.get_by_id = MagicMock(return_value=(sample_payment_method)) # in this test don't care of the return value, the most important thing is that the function does not raise NotFound exception
        mock_account_manager.get_by_name = MagicMock(side_effect=AccountNotFoundError(""))

        with pytest.raises(AccountNotFoundError):
            subscription_manager.add_payment_record(sample_membership_empty, False)

        mock_payment_method_manager.get_by_id.assert_called_once()
        mock_account_manager.get_by_name.assert_called()

    def test_no_src_account(self,
                        mock_payment_method_manager: PaymentMethodManager,
                        mock_account_manager: AccountManager,
                        subscription_manager: SubscriptionManager,
                        sample_membership_empty: Membership,
                        sample_account1: Account,
                        sample_payment_method: PaymentMethod):
        mock_payment_method_manager.get_by_id = MagicMock(return_value=(sample_payment_method)) # in this test don't care of the return value, the most important thing is that the function does not raise NotFound exception
        mock_account_manager.get_by_name = MagicMock(side_effect=AccountNotFoundError(""))

        with pytest.raises(AccountNotFoundError):
            subscription_manager.add_payment_record(sample_membership_empty, False)

        mock_payment_method_manager.get_by_id.assert_called_once()
        mock_account_manager.get_by_name.assert_called()

    def test_no_room(self,
                        mock_payment_method_manager: PaymentMethodManager,
                        mock_account_manager: AccountManager,
                        mock_transaction_manager: TransactionManager,
                        subscription_manager: SubscriptionManager,
                        sample_membership_pending_payment_validation: Membership,
                        sample_account1: Account,
                        sample_payment_method: PaymentMethod):
        mock_payment_method_manager.get_by_id = MagicMock(return_value=(sample_payment_method)) # in this test don't care of the return value, the most important thing is that the function does not raise NotFound exception
        mock_account_manager.get_by_name = MagicMock(return_value=(sample_account1))
        mock_transaction_manager.update_or_create = MagicMock(return_value=(None))

        sample_membership_pending_payment_validation.has_room = False

        subscription_manager.add_payment_record(sample_membership_pending_payment_validation, False)

        mock_payment_method_manager.get_by_id.assert_called_once()
        mock_account_manager.get_by_name.assert_called()
        mock_transaction_manager.update_or_create.assert_called_once()

    def test_free(self,
                        mock_payment_method_manager: PaymentMethodManager,
                        mock_account_manager: AccountManager,
                        mock_transaction_manager: TransactionManager,
                        subscription_manager: SubscriptionManager,
                        sample_membership_pending_payment_validation: Membership,
                        sample_account1: Account,
                        sample_payment_method: PaymentMethod):
        mock_payment_method_manager.get_by_id = MagicMock(return_value=(sample_payment_method)) # in this test don't care of the return value, the most important thing is that the function does not raise NotFound exception
        mock_account_manager.get_by_name = MagicMock(return_value=(sample_account1))
        mock_transaction_manager.update_or_create = MagicMock(return_value=(None))

        subscription_manager.add_payment_record(sample_membership_pending_payment_validation, True)

        mock_payment_method_manager.get_by_id.assert_called_once()
        mock_account_manager.get_by_name.assert_called()
        mock_transaction_manager.update_or_create.assert_called_once()




@pytest.fixture
def subscription_manager(
        mock_member_repository,
        mock_subscription_repository,
        mock_charter_manager,
        mock_account_manager,
        mock_payment_method_manager,
        mock_transaction_manager,
        mock_notification_manager,
):
    return SubscriptionManager(
        member_repository = mock_member_repository,
        membership_repository = mock_subscription_repository,
        charter_manager = mock_charter_manager,
        notification_manager = mock_notification_manager,
        account_manager = mock_account_manager,
        payment_method_manager = mock_payment_method_manager,
        transaction_manager = mock_transaction_manager
    )


@pytest.fixture
def mock_member_repository():
    return MagicMock(spec=MemberRepository)


@pytest.fixture
def mock_subscription_repository():
    return MagicMock(spec=MembershipRepository)


@pytest.fixture
def mock_charter_manager():
    return MagicMock(spec=CharterManager)


@pytest.fixture
def mock_notification_manager():
    return MagicMock(spec=NotificationManager)


@pytest.fixture
def mock_transaction_manager():
    return MagicMock(spec=TransactionManager)


@pytest.fixture
def mock_payment_method_manager():
    return MagicMock(spec=PaymentMethodManager)


@pytest.fixture
def mock_account_manager():
    return MagicMock(spec=AccountManager)

@pytest.fixture
def sample_subscription_pending_rules(sample_member):
    return Membership(
        uuid="",
        member=sample_member,
        status=MembershipStatus.PENDING_RULES.value
    )

@pytest.fixture
def sample_subscription_pending_payment_initial(sample_member):
    return Membership(
        uuid="",
        member=sample_member,
        status=MembershipStatus.PENDING_PAYMENT_INITIAL.value
    )

@pytest.fixture
def sample_subscription_pending_payment(sample_member):
    return Membership(
        uuid="",
        member=sample_member,
        status=MembershipStatus.PENDING_PAYMENT.value,
        duration=MembershipDuration.ONE_YEAR.value
    )

@pytest.fixture
def sample_subscription_pending_payment_validation(sample_member, sample_account1, sample_payment_method):
    return Membership(
        uuid="",
        member=sample_member,
        status=MembershipStatus.PENDING_PAYMENT_VALIDATION.value,
        duration=MembershipDuration.ONE_YEAR.value,
        account=sample_account1.id,
        payment_method=sample_payment_method.id
    )

@pytest.fixture
def sample_membership_pending_rules(sample_member):
    return Membership(
        uuid="",
        member=sample_member,
        status=MembershipStatus.PENDING_RULES.value,
    )

@pytest.fixture
def sample_membership_pending_payment_initial(sample_member):
    return Membership(
        uuid="",
        member=sample_member,
        status=MembershipStatus.PENDING_PAYMENT_INITIAL.value,
    )

@pytest.fixture
def sample_membership_pending_payment(sample_member):
    return Membership(
        uuid="",
        member=sample_member,
        status=MembershipStatus.PENDING_PAYMENT.value,
        duration=MembershipDuration.ONE_YEAR.value,
    )

@pytest.fixture
def sample_membership_pending_payment_validation(sample_member, sample_account1, sample_payment_method):
    return Membership(
        uuid="",
        member=sample_member,
        status=MembershipStatus.PENDING_PAYMENT_VALIDATION.value,
        duration=MembershipDuration.ONE_YEAR.value,
        account=sample_account1.id,
        payment_method=sample_payment_method.id,
    )
