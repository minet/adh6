import datetime
from unittest.mock import MagicMock

from pytest import fixture

from src.entity import AccountType
from src.entity.account import Account
from src.entity.admin import Admin
from src.entity.device import Device
from src.entity.member import Member
from src.entity.payment_method import PaymentMethod
from src.entity.port import Port
from src.entity.product import Product
from src.entity.roles import Roles
from src.entity.room import Room
from src.entity.switch import Switch
from src.entity.transaction import Transaction
from src.interface_adapter.http_api.auth import TESTING_CLIENT
from src.use_case.interface.account_repository import AccountRepository
from src.util.context import build_context

def pytest_configure(config):
    import sys
    sys._called_from_unit_test = True

def pytest_unconfigure(config):
    import sys  # This was missing from the manual
    del sys._called_from_unit_test

@fixture
def ctx(sample_member):
    return build_context(
        admin=sample_member,
        testing=True,
        roles=[Roles.ADH6_USER, Roles.ADH6_ADMIN, Roles.ADH6_SUPER_ADMIN, Roles.ADH6_TRESO]
    )


@fixture
def sample_admin():
    return Admin(
        login=TESTING_CLIENT,
        roles=[]
    )


@fixture
def sample_member(faker, sample_room):
    return Member(
        id=faker.random_digit_not_null,
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
def sample_member_no_room(faker, sample_room):
    return Member(
        id=faker.random_digit_not_null,
        username=faker.user_name,
        email=faker.email,
        first_name=faker.first_name,
        last_name=faker.last_name,
        departure_date=faker.date_this_year(after_today=True).isoformat(),
        comment=faker.sentence,
        association_mode=faker.date_time_this_year(after_now=True).isoformat(),
        room=None,
    )

@fixture
def sample_device(faker, sample_member):
    return Device(
        id=faker.random_digit_not_null,
        mac=faker.mac_address().replace(":", "-"),
        member=sample_member,
        connection_type='wired',
        ipv4_address=faker.ipv4(address_class='157.159.41.0/24'),
        ipv6_address=faker.ipv6(),
    )


@fixture
def sample_room(faker):
    return Room(
        id=faker.random_digit_not_null,
        room_number=faker.numerify(text='####'),
        description='Test room.',
        vlan=41,
    )


@fixture
def sample_port(faker, sample_room, sample_switch):
    return Port(
        id=faker.random_digit_not_null,
        port_number=faker.numerify(text='#/#/##'),
        room=sample_room,
        switch_obj=sample_switch,
        oid=10101,
    )


@fixture
def sample_switch(faker):
    return Switch(
        id=faker.random_digit_not_null,
        ip=faker.ipv4_private,
        description=faker.sentence,
        community=faker.password,
    )


@fixture
def sample_payment_method(faker):
    return PaymentMethod(
        id=faker.random_digit_not_null,
        name=faker.word
    )


@fixture
def sample_account_type(faker):
    return AccountType(
        id=faker.random_digit_not_null,
        name=faker.word
    )


@fixture
def sample_transaction(faker, sample_admin, sample_account1, sample_account2):
    return Transaction(
        id=faker.random_digit_not_null,
        src=sample_account1,
        dst=sample_account2,
        name=faker.sentence,
        value=faker.random_int,
        attachments='',
        timestamp=faker.date_this_year,
        payment_method=sample_payment_method,
        author=sample_admin
    )


@fixture
def sample_transaction_pending(faker, sample_admin, sample_account1, sample_account2):
    return Transaction(
        id=faker.random_digit_not_null,
        src=sample_account1,
        dst=sample_account2,
        name=faker.sentence,
        value=faker.random_int,
        attachments='',
        timestamp=faker.date_this_year,
        payment_method=sample_payment_method,
        author=sample_admin,
        pending_validation=True
    )

@fixture
def sample_account1(faker, sample_member, sample_account_type):
    return Account(
        id=faker.random_digit_not_null,
        name=faker.word,
        actif=faker.random_choices(elements=(True, False)),
        creation_date=faker.date_this_year,
        member=sample_member,
        balance=0,
        compte_courant=faker.random_choices(elements=(True, False)),
        pinned=faker.random_choices(elements=(True, False)),
        account_type=sample_account_type,
        pending_balance=faker.random_int
    )


@fixture
def sample_account2(faker, sample_member, sample_account_type):
    return Account(
        id=faker.random_digit_not_null,
        name=faker.word,
        actif=faker.random_choices(elements=(True, False)),
        creation_date=faker.date_this_year,
        member=sample_member,
        balance=0,
        compte_courant=faker.random_choices(elements=(True, False)),
        pinned=faker.random_choices(elements=(True, False)),
        account_type=sample_account_type,
        pending_balance=faker.random_int
    )


@fixture
def sample_product(faker):
    return Product(
        id=faker.random_digit_not_null,
        name=faker.word,
        selling_price=faker.random_int,
        buying_price=faker.random_int
    )
