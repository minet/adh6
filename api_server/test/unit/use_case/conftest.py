from adh6.constants import MembershipStatus

from pytest import fixture

from adh6.entity import (
    AccountType,
    Account,
    Device,
    Member,
    PaymentMethod,
    Port,
    Product,
    Room,
    Switch,
    Transaction,
    AbstractMembership,
    Vlan
)
from adh6.authentication import Roles
from adh6.entity.subscription_body import SubscriptionBody
from test import TESTING_CLIENT
from adh6.misc.context import build_context

@fixture(autouse=True)
def mock_missing_default_user(monkeypatch):
    import connexion
    """Remove the user key from DEFAULT_CONFIG"""
    monkeypatch.setattr(connexion, "context", {"token_info": ""}, raising=False)

@fixture(autouse=True)
def app_context(monkeypatch):
    monkeypatch.setenv("UNIT_TESTING", "test")

@fixture(autouse=True)
def mock_test_configuration(monkeypatch):
    from adh6.member.member_manager import MemberManager
    monkeypatch.setattr(MemberManager, "duration_price", {1:9, 12: 50})
    monkeypatch.setattr(MemberManager, "duration_string", {1:'1 Mois', 12: '1 an'})

@fixture
def ctx(sample_member: Member):
    return build_context(
        admin=sample_member.id,
        testing=True,
        roles=[Roles.USER.value, Roles.ADMIN_WRITE.value, Roles.ADMIN_READ.value, Roles.TRESO_WRITE.value, Roles.TRESO_READ.value]
    )


@fixture
def ctx_only_admin(sample_member: Member):
    return build_context(
        admin=sample_member.id,
        testing=True,
        roles=[Roles.USER.value, Roles.ADMIN_WRITE.value, Roles.ADMIN_READ.value]
    )


@fixture
def sample_admin(faker):
    yield Member(
        id=faker.random_digit_not_null(),
        username=TESTING_CLIENT,
        email=faker.email(),
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        departure_date=faker.date_this_year(after_today=True).isoformat(),
    )


@fixture
def sample_member(faker):
    return Member(
        id=faker.random_digit_not_null(),
        username=faker.user_name(),
        email=faker.email(),
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        departure_date=faker.date_this_year(after_today=True).isoformat(),
        comment=faker.sentence(),
    )


@fixture
def sample_vlan(faker):
    return Vlan(
        id=faker.random_digit_not_null(),
        number=faker.random_digit_not_null(),
        ipv4_network="157.159.41.0/24",
        ipv6_network="fe80::/64"
    )

@fixture
def sample_subscription_empty(sample_member):
    return SubscriptionBody(
        member=sample_member,
    )

@fixture
def sample_subscription_duration_no_account(sample_member):
    return SubscriptionBody(
        member=sample_member,
        duration=1
    )

@fixture
def sample_subscription_duration_account_payment_method(sample_member, sample_account1, sample_payment_method):
    return SubscriptionBody(
        member=sample_member,
        duration=1,
        account=sample_account1.id,
        payment_method=sample_payment_method.id
    )

@fixture
def sample_membership_empty(sample_member):
    return AbstractMembership(
        uuid="",
        member=sample_member,
        status=MembershipStatus.INITIAL.value
    )

@fixture
def sample_membership_duration_no_account(sample_member):
    return AbstractMembership(
        uuid="",
        member=sample_member,
        status=MembershipStatus.INITIAL.value,
        duration=1
    )

@fixture
def sample_membership_duration_account_payment_method(sample_member, sample_account1, sample_payment_method):
    return AbstractMembership(
        uuid="",
        member=sample_member,
        status=MembershipStatus.INITIAL.value,
        duration=1,
        account=sample_account1.id,
        payment_method=sample_payment_method.id
    )


@fixture
def sample_member_no_room(faker):
    return Member(
        id=faker.random_digit_not_null(),
        username=faker.user_name(),
        email=faker.email(),
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        departure_date=faker.date_this_year(after_today=True).isoformat(),
        comment=faker.sentence(),
    )


@fixture
def sample_device(faker, sample_member):
    return Device(
        id=faker.random_digit_not_null(),
        mac=faker.mac_address().replace(":", "-"),
        member=sample_member,
        connection_type='wired',
        ipv4_address=faker.ipv4(address_class='157.159.41.0/24'),
        ipv6_address=faker.ipv6(),
    )


@fixture
def sample_room(faker):
    return Room(
        id=faker.random_digit_not_null(),
        room_number=faker.numerify(text='####'),
        description='Test room.',
        vlan=41,
    )


@fixture
def sample_port(faker, sample_room, sample_switch):
    return Port(
        id=faker.random_digit_not_null(),
        port_number=faker.numerify(text='#/#/##'),
        room=sample_room,
        switch_obj=sample_switch,
        oid=10101,
    )


@fixture
def sample_switch(faker):
    return Switch(
        id=faker.random_digit_not_null(),
        ip=faker.ipv4_private(),
        description=faker.sentence(),
        community=faker.password(),
    )


@fixture
def sample_payment_method(faker):
    return PaymentMethod(
        id=faker.random_digit_not_null(),
        name=faker.word()
    )


@fixture
def sample_account_type(faker):
    return AccountType(
        id=faker.random_digit_not_null(),
        name=faker.word()
    )


@fixture
def sample_transaction(faker, sample_admin, sample_account1, sample_account2, sample_payment_method):
    yield Transaction(
        id=faker.random_digit_not_null(),
        src=sample_account1.id,
        dst=sample_account2.id,
        name=faker.sentence(),
        value=faker.random_int(),
        attachments='',
        timestamp=faker.date_this_year(),
        payment_method=sample_payment_method.id,
        author=sample_admin.id
    )


@fixture
def sample_transaction_pending(faker, sample_admin, sample_account1, sample_account2, sample_payment_method):
    yield Transaction(
        id=faker.random_digit_not_null(),
        src=sample_account1.id,
        dst=sample_account2.id,
        name=faker.sentence(),
        value=faker.random_int(),
        attachments='',
        timestamp=faker.date_this_year(),
        payment_method=sample_payment_method.id,
        author=sample_admin.id,
        pending_validation=True
    )

@fixture
def sample_account1(faker, sample_member, sample_account_type):
    yield Account(
        id=faker.random_digit_not_null(),
        name=faker.word(),
        actif=faker.random_choices(elements=(True, False)),
        creation_date=faker.date_this_year(),
        member=sample_member,
        balance=0,
        compte_courant=faker.random_choices(elements=(True, False)),
        pinned=faker.random_choices(elements=(True, False)),
        account_type=sample_account_type,
        pending_balance=faker.random_int()
    )


@fixture
def sample_account2(faker, sample_member, sample_account_type):
    return Account(
        id=faker.random_digit_not_null() + 1024,
        name=faker.word(),
        actif=faker.random_choices(elements=(True, False)),
        creation_date=faker.date_this_year(),
        member=sample_member,
        balance=0,
        compte_courant=faker.random_choices(elements=(True, False)),
        pinned=faker.random_choices(elements=(True, False)),
        account_type=sample_account_type,
        pending_balance=faker.random_int()
    )


@fixture
def sample_product(faker):
    return Product(
        id=faker.random_digit_not_null(),
        name=faker.word(),
        selling_price=faker.random_int(),
        buying_price=faker.random_int()
    )
