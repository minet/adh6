from collections.abc import Generator
from os import name

from adh6.authentication import Roles
from adh6.constants import MembershipStatus
from adh6.entity import (
    AbstractMembership,
    Account,
    AccountType,
    Device,
    Member,
    PaymentMethod,
    Port,
    Product,
    Room,
    Switch,
    Transaction,
    Vlan,
)
from adh6.entity.subscription_body import SubscriptionBody
from pytest import fixture

from test import TESTING_CLIENT


@fixture(autouse=True)
def mock_test_configuration(monkeypatch):
    from adh6.member.subscription_manager import SubscriptionManager

    monkeypatch.setattr(SubscriptionManager, "duration_price", {1: 9, 12: 50})
    monkeypatch.setattr(
        SubscriptionManager, "duration_string", {1: "1 Mois", 12: "1 an"}
    )


@fixture(autouse=True)
def ctx(sample_member: Member, monkeypatch):
    import adh6.context as context

    monkeypatch.setattr(context, "get_user", lambda: sample_member.id, raising=False)
    monkeypatch.setattr(
        context,
        "get_roles",
        lambda: [
            Roles.USER.value,
            Roles.ADMIN_WRITE.value,
            Roles.ADMIN_READ.value,
            Roles.TRESO_WRITE.value,
            Roles.TRESO_READ.value,
        ],
        raising=False,
    )


@fixture
def ctx_only_admin(sample_member: Member, monkeypatch):
    import adh6.context as context

    monkeypatch.setattr(context, "get_user", lambda: sample_member.id, raising=False)
    monkeypatch.setattr(
        context,
        "get_roles",
        lambda: [Roles.USER.value, Roles.ADMIN_WRITE.value, Roles.ADMIN_READ.value],
        raising=False,
    )


@fixture
def sample_admin(faker) -> Generator[Member, None, None]:
    yield Member(
        id=faker.random_digit_not_null(),
        username=TESTING_CLIENT,
        email=faker.email(),
        firstName=faker.first_name(),
        lastName=faker.last_name(),
        departureDate=faker.date_this_year(after_today=True).isoformat(),
    )


@fixture
def sample_member(faker) -> Member:
    return Member(
        id=faker.random_digit_not_null(),
        username=faker.user_name(),
        email=faker.email(),
        firstName=faker.first_name(),
        lastName=faker.last_name(),
        departureDate=faker.date_this_year(after_today=True).isoformat(),
        comment=faker.sentence(),
    )


@fixture
def sample_vlan(faker) -> Vlan:
    return Vlan(
        id=faker.random_digit_not_null(),
        number=faker.random_digit_not_null(),
        ipv4Network="157.159.41.0/24",
        ipv6Network="fe80::/64",
    )


@fixture
def sample_subscription_empty(sample_member) -> SubscriptionBody:
    return SubscriptionBody(
        member=sample_member.id,
    )


@fixture
def sample_subscription_duration_no_account(sample_member) -> SubscriptionBody:
    return SubscriptionBody(member=sample_member.id, duration=1)


@fixture
def sample_subscription_duration_account_payment_method(
    sample_member, sample_account1, sample_payment_method
) -> SubscriptionBody:
    return SubscriptionBody(
        member=sample_member.id,
        duration=1,
        account=sample_account1.id,
        paymentMethod=sample_payment_method.id,
    )


@fixture
def sample_membership_empty(sample_member) -> AbstractMembership:
    return AbstractMembership(
        uuid="", member=sample_member.id, status=MembershipStatus.INITIAL.value
    )


@fixture
def sample_membership_duration_no_account(sample_member) -> AbstractMembership:
    return AbstractMembership(
        uuid="",
        member=sample_member.id,
        status=MembershipStatus.INITIAL.value,
        duration=1,
    )


@fixture
def sample_membership_duration_account_payment_method(
    sample_member, sample_account1, sample_payment_method
) -> AbstractMembership:
    return AbstractMembership(
        uuid="",
        member=sample_member.id,
        status=MembershipStatus.INITIAL.value,
        duration=1,
        account=sample_account1.id,
        paymentMethod=sample_payment_method.id,
    )


@fixture
def sample_member_no_room(faker) -> Member:
    return Member(
        id=faker.random_digit_not_null(),
        username=faker.user_name(),
        email=faker.email(),
        firstName=faker.first_name(),
        lastName=faker.last_name(),
        departureDate=faker.date_this_year(after_today=True).isoformat(),
        comment=faker.sentence(),
    )


@fixture
def sample_device(faker, sample_member) -> Device:
    return Device(
        id=faker.random_digit_not_null(),
        mac=faker.mac_address().replace(":", "-"),
        member=sample_member.id,
        connectionType="wired",
        ipv4Address=faker.ipv4(address_class="157.159.41.0/24"),
        ipv6Address=faker.ipv6(),
    )


@fixture
def sample_room(faker) -> Room:
    return Room(
        id=faker.random_digit_not_null(),
        roomNumber=faker.numerify(text="####"),
        description="Test room.",
        vlan=41,
    )


@fixture
def sample_port(faker, sample_room, sample_switch) -> Port:
    return Port(
        id=faker.random_digit_not_null(),
        portNumber=faker.numerify(text="#/#/##"),
        room=sample_room,
        switchObj=sample_switch,
        oid="10101",
    )


@fixture
def sample_switch(faker) -> Switch:
    return Switch(
        id=faker.random_digit_not_null(),
        ip=faker.ipv4_private(),
        description=faker.sentence(),
        community=faker.password(),
    )


@fixture
def sample_payment_method(faker) -> PaymentMethod:
    return PaymentMethod(id=faker.random_digit_not_null(), name=faker.word())


@fixture
def sample_account_type(faker) -> AccountType:
    return AccountType(id=faker.random_digit_not_null(), name=faker.word())


@fixture
def sample_transaction(
    faker, sample_admin, sample_account1, sample_account2, sample_payment_method
):
    yield Transaction(
        id=faker.random_digit_not_null(),
        src=sample_account1.id,
        dst=sample_account2.id,
        name=faker.sentence(),
        value=faker.random_int(),
        attachments="",
        timestamp=faker.date_this_year(),
        paymentMethod=sample_payment_method.id,
        author=sample_admin.id,
    )


@fixture
def sample_transaction_pending(
    faker, sample_admin, sample_account1, sample_account2, sample_payment_method
):
    yield Transaction(
        id=faker.random_digit_not_null(),
        src=sample_account1.id,
        dst=sample_account2.id,
        name=faker.sentence(),
        value=faker.random_int(),
        attachments="",
        timestamp=faker.date_this_year(),
        paymentMethod=sample_payment_method.id,
        author=sample_admin.id,
        pendingValidation=True,
    )


@fixture
def sample_account1(faker, sample_member, sample_account_type):
    yield Account(
        id=faker.random_digit_not_null(),
        name=faker.word(),
        actif=faker.boolean(),
        creationDate=faker.date_this_year(),
        member=sample_member.id,
        balance=0,
        compteCourant=faker.boolean(),
        pinned=faker.boolean(),
        accountType=sample_account_type.id,
        pendingBalance=faker.random_int(),
    )


@fixture
def sample_account2(faker, sample_member, sample_account_type) -> Account:
    return Account(
        id=faker.random_digit_not_null() + 1024,
        name=faker.word(),
        actif=faker.boolean(),
        creationDate=faker.date_this_year(),
        member=sample_member.id,
        balance=0,
        compteCourant=faker.boolean(),
        pinned=faker.boolean(),
        accountType=sample_account_type.id,
        pendingBalance=faker.random_int(),
    )


@fixture
def sample_product(faker) -> Product:
    return Product(
        id=faker.random_digit_not_null(),
        name=faker.word(),
        sellingPrice=faker.random_int(),
        buyingPrice=faker.random_int(),
    )
