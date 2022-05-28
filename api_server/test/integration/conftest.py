from datetime import datetime
from uuid import uuid4
import pytest
from src.constants import MembershipDuration, MembershipStatus
from src.use_case.decorator.security import Roles
from test.integration.resource import api_key
from test.auth import SAMPLE_CLIENT, SAMPLE_CLIENT2, TESTING_CLIENT
from src.interface_adapter.sql.device_repository import DeviceType
from src.interface_adapter.sql.model.models import (
    Account,
    ApiKey,
    Membership,
    AccountType, Adherent, Chambre,
    PaymentMethod, Vlan, Device, Switch, Port
)
from test.integration.context import tomorrow

def prep_db(*args):
    from src.interface_adapter.sql.model.models import db as _db
    _db.create_all()
    session = _db.session()
    session.add_all(args)
    session.add(sample_member_admin())
    session.add(sample_api_key())
    session.commit()

def close_db():
    from src.interface_adapter.sql.model.models import db as _db
    _db.session.close()
    _db.drop_all()


@pytest.fixture
def client(sample_member, sample_member2, sample_member13,
        wired_device, wireless_device,
        account_type, sample_payment_method, sample_account_frais_asso, sample_account_frais_techniques,
        sample_room1, sample_room2, sample_vlan, sample_account, sample_complete_membership, sample_pending_validation_membership):
    from .context import app
    if app.app is None:
        return
    with app.app.test_client() as c:
        prep_db(
            sample_member,
            sample_member2,
            sample_member13,
            sample_payment_method,
            wired_device,
            wireless_device,
            account_type,
            sample_room1,
            sample_room2,
            sample_vlan,
            sample_account,
            sample_account_frais_asso,
            sample_account_frais_techniques,
            sample_complete_membership,
            sample_pending_validation_membership
        )
        yield c
        close_db()


@pytest.fixture
def account_type(faker):
    yield AccountType(
        id=faker.random_digit_not_null(),
        name="Adhérent"
    )

@pytest.fixture
def sample_account(account_type: AccountType, sample_member: Adherent):
    yield Account(
        type=account_type.id,
        creation_date=datetime.now(),
        name="account",
        actif=True,
        compte_courant=False,
        pinned=False,
        adherent=sample_member
    )

@pytest.fixture
def sample_account_frais_asso(account_type: AccountType):
    yield Account(
        type=account_type.id,
        creation_date=datetime.now(),
        name="MiNET frais asso",
        actif=True,
        compte_courant=True,
        pinned=True
    )

@pytest.fixture
def sample_account_frais_techniques(account_type: AccountType):
    yield Account(
        type=account_type.id,
        creation_date=datetime.now(),
        name="MiNET frais techniques",
        actif=True,
        compte_courant=True,
        pinned=True
    )

@pytest.fixture
def sample_payment_method():
    return PaymentMethod(
        id=1,
        name='liquide'
    )


@pytest.fixture
def wired_device(faker, sample_member):
    yield Device(
        id=faker.random_digit_not_null(),
        mac=faker.mac_address(),
        adherent=sample_member,
        type=DeviceType.wired.value,
        ip=faker.ipv4_public(),
        ipv6=faker.ipv6(),
    )


@pytest.fixture
def wired_device2(faker, sample_member):
    yield Device(
        id=faker.random_digit_not_null(),
        mac=faker.mac_address(),
        adherent=sample_member,
        type=DeviceType.wired.value,
        ip=faker.ipv4_public(),
        ipv6=faker.ipv6(),
    )


@pytest.fixture
def wireless_device(faker, sample_member):
    yield Device(
        id=faker.random_digit_not_null(),
        mac=faker.mac_address(),
        adherent=sample_member,
        type=DeviceType.wireless.value,
        ip=faker.ipv4_private(),
        ipv6=faker.ipv6(),
    )


@pytest.fixture
def wireless_device_dict(sample_member):
    '''
    Device that will be inserted/updated when tests are run.
    It is not present in the client by default
    '''
    yield {
        'mac': '01-23-45-67-89-AC',
        'connectionType': 'wireless',
        'type': 'wireless',
        'member': sample_member.id,
        'ipv4Address': None,
        'ipv6Address': None
    }


@pytest.fixture
def wired_device_dict(sample_member):
    yield {
        'mac': '01-23-45-67-89-AD',
        'ipv4Address': '127.0.0.1',
        'ipv6Address': 'dbb1:39b7:1e8f:1a2a:3737:9721:5d16:166',
        'connectionType': 'wired',
        'type': 'wired',
        'member': sample_member.id,
    }


@pytest.fixture
def sample_vlan():
    yield Vlan(
        numero=42,
        adresses="192.168.42.0/24",
        adressesv6="fe80::0/64",
    )


@pytest.fixture
def sample_room1(sample_vlan):
    yield Chambre(
        numero=5110,
        description="Chambre de l'ambiance",
        vlan=sample_vlan,
    )


@pytest.fixture
def sample_room2(sample_vlan):
    yield Chambre(
        numero=4592,
        description="Chambre voisine du swag",
        vlan=sample_vlan,
    )


def sample_member_admin():
    return Adherent(
        login=TESTING_CLIENT,
        mail="test@example.com",
        nom="Test",
        prenom="test",
        password="",
    )


def sample_api_key():
    return ApiKey(
        name="api_key",
        uuid=api_key,
        role=Roles.SUPERADMIN.value
    )

@pytest.fixture
def sample_complete_membership(sample_account: Account, sample_member: Adherent, ):
    yield Membership(
        uuid=str(uuid4()),
        account_id=sample_account.id,
        create_at=datetime.now(),
        duration=MembershipDuration.ONE_YEAR,
        has_room=True,
        first_time=True,
        adherent=sample_member,
        status=MembershipStatus.COMPLETE,
        update_at=datetime.now(),
        products="[]"
    )

@pytest.fixture
def sample_pending_validation_membership(sample_account: Account, sample_member2: Adherent):
    """ Membership that is not completed """
    yield Membership(
        uuid=str(uuid4()),
        account_id=sample_account.id,
        create_at=datetime.now(),
        duration=MembershipDuration.ONE_YEAR,
        has_room=True,
        first_time=True,
        adherent=sample_member2,
        status=MembershipStatus.PENDING_PAYMENT_VALIDATION,
        update_at=datetime.now(),
        products="[]"
    )

# Member that have an account and a membership
@pytest.fixture
def sample_member(faker, sample_room1):
    yield Adherent(
        nom='Dubois',
        prenom='Jean-Louis',
        mail='j.dubois@free.fr',
        login=SAMPLE_CLIENT,
        password='a',
        chambre=sample_room1,
        date_de_depart=tomorrow,
        datesignedminet=datetime.now(),
        ip=faker.ipv4_public(),
        subnet=faker.ipv4('c')
    )


@pytest.fixture
def sample_member2(sample_room1):
    yield Adherent(
        nom='Reignier',
        prenom='Edouard',
        mail='bgdu78@hotmail.fr',
        login='reignier',
        commentaires='Desauthent pour routeur',
        password='a',
        chambre=sample_room1,
        date_de_depart=tomorrow,
    )


@pytest.fixture
def sample_member3(sample_room1):
    yield Adherent(
        nom='Dupont',
        prenom='Jean',
        mail='test@oyopmail.fr',
        login=SAMPLE_CLIENT2,
        commentaires='abcdef',
        password='b',
        chambre=sample_room1,
        date_de_depart=tomorrow,
    )


@pytest.fixture
def sample_member13():
    """ Membre sans chambre """
    yield Adherent(
        nom='Robert',
        prenom='Dupond',
        mail='robi@hotmail.fr',
        login='dupond_r',
        commentaires='a',
        password='a',
        date_de_depart=tomorrow,
    )


@pytest.fixture
def sample_switch1():
    yield Switch(
        description="Switch sample 1",
        ip="192.168.102.51",
        communaute="GrosMotDePasse",
    )


@pytest.fixture
def sample_switch2():
    yield Switch(
        description="Switch sample 2",
        ip="192.168.102.52",
        communaute="GrosMotDePasse",
    )


@pytest.fixture
def sample_port1(sample_switch1):
    yield Port(
        rcom=1,
        numero="0/0/1",
        oid="1.1.1",
        switch=sample_switch1,
        chambre_id=1,
    )


@pytest.fixture
def sample_port2(sample_switch2):
    yield Port(
        rcom=2,
        numero="0/0/2",
        oid="1.1.2",
        switch=sample_switch2,
        chambre_id=1,

    )
