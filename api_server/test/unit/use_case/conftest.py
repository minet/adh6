import datetime

from pytest import fixture

from src.entity.account import Account
from src.entity.admin import Admin
from src.entity.device import Device
from src.entity.member import Member
from src.entity.payment_method import PaymentMethod
from src.entity.port import Port
from src.entity.product import Product
from src.entity.room import Room
from src.entity.switch import Switch
from src.entity.transaction import Transaction
from src.interface_adapter.http_api.auth import TESTING_CLIENT
from src.util.context import build_context


@fixture
def ctx():
    return build_context(
        admin=Admin(login='test_usr'),
        testing=True,
    )


TEST_USERNAME = 'test_usr'
TEST_EMAIL = 'hello@hello.fr'
TEST_FIRST_NAME = 'Jean'
TEST_LAST_NAME = 'Dupond'
TEST_COMMENT = 'This is a comment.'
TEST_ROOM_NUMBER = '1234'
TEST_DATE1 = datetime.datetime.fromisoformat('2019-04-21T11:11:46')
TEST_DATE2 = datetime.datetime.fromisoformat('2000-01-01T00:00:00')
TEST_LOGS = [
    'hello',
    'hi',
]
TEST_MAC_ADDRESS1 = 'A0-B1-5A-C1-5F-E3'
TEST_MAC_ADDRESS2 = '10-0E-9C-19-FF-64'


@fixture
def sample_admin():
    return Admin(
        login=TESTING_CLIENT
    )

@fixture
def sample_member():
    return Member(
        username=TEST_USERNAME,
        email=TEST_EMAIL,
        first_name=TEST_FIRST_NAME,
        last_name=TEST_LAST_NAME,
        departure_date=TEST_DATE1.isoformat(),
        comment=TEST_COMMENT,
        association_mode=TEST_DATE2.isoformat(),
        room_number=str(TEST_ROOM_NUMBER),
    )


@fixture
def sample_device():
    return Device(
        mac_address='FF-FF-FF-FF-FF-FF',
        owner_username=TEST_USERNAME,
        connection_type='wired',
        ip_v4_address='127.0.0.1',
        ip_v6_address='127.0.0.1',
    )


@fixture
def sample_room():
    return Room(
        room_number=1234,
        description='Test room.',
        vlan=41,
    )


@fixture
def sample_port(sample_room, sample_switch):
    return Port(
        id="1",
        port_number="test number",
        room=sample_room,
        switch=sample_switch,
        oid=10101,
    )


@fixture
def sample_switch():
    return Switch(
        id='1',
        ip='127.0.0.1',
        description='description',
        community='community',
    )


@fixture
def sample_payment_method():
    return PaymentMethod(
        id=0,
        name='liquide'
    )


@fixture
def sample_transaction(sample_admin):
    return Transaction(
        src=Account(
            name="Test",
            type=1,
            actif=True,
            creation_date='21/05/2019',
            account_id=1,
            adherent=None,
            balance=None,
            compte_courant=False,
            pinned = False
        ),
        dst=Account(
            name="Test2",
            type=1,
            actif=True,
            creation_date='21/05/2019',
            account_id=2,
            adherent=None,
            balance=None,
            compte_courant=False,
            pinned=False
        ),
        name='description',
        value='200',
        attachments='',
        timestamp='',
        paymentMethod=PaymentMethod(
            id=0,
            name='liquide'
        ),
        author=sample_admin)


@fixture
def sample_account():
    return Account(
        name='MiNET',
        type=1,
        actif=True,
        creation_date='21/05/2019',
        account_id=1,
        adherent = None,
        balance=None,
        compte_courant=False,
        pinned=False
    )


@fixture
def sample_product():
    return Product(
        name='loutre',
        selling_price=9999,
        buying_price=999,
        id=1
    )