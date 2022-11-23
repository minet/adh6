from datetime import datetime, timedelta
from uuid import uuid4
from adh6.authentication import AuthenticationMethod
from adh6.device.storage import DeviceType
import pytest
from adh6.constants import MembershipDuration, MembershipStatus
from adh6.authentication import Roles
from test.integration.resource import TEST_HEADERS, TEST_HEADERS_API_KEY_ADMIN, TEST_HEADERS_API_KEY_USER
from test import SAMPLE_CLIENT_ID, TESTING_CLIENT, SAMPLE_CLIENT, TESTING_CLIENT_ID
from adh6.treasury.storage.models import AccountType, Account, PaymentMethod
from adh6.member.storage.models import Adherent, Membership
from adh6.device.storage.models import Device
from adh6.room.storage.models import Chambre, RoomMemberLink
from adh6.subnet.storage.models import Vlan
from adh6.network.storage.models import Switch, Port
from adh6.authentication.storage.models import ApiKey, AuthenticationRoleMapping
from test.integration.context import tomorrow
from hashlib import sha512

m = sha512()

def prep_db(*args):
    from adh6.storage.sql.models import db as _db
    _db.create_all()
    session = _db.session()
    session.add(sample_member_admin())
    session.add_all(
        [
            oidc_admin_prod_role(),
            oidc_admin_read_role(),
            oidc_admin_write_role(),
            oidc_network_read_role(),
            oidc_network_write_role(),
            oidc_treasurer_read_role(),
            oidc_treasurer_write_role()
        ]
    )
    session.add_all(args)
    session.add_all(
        [
            api_key_admin(),
        ] + 
        [
            api_key_admin_read_roles(),
            api_key_admin_write_roles()
        ]
    )
    session.commit()

def close_db():
    from adh6.storage.sql.models import db as _db
    _db.session.close()
    _db.drop_all()


@pytest.fixture
def client(sample_member, sample_member2, sample_member13,
        wired_device, wireless_device, sample_room_member_link,
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
            sample_pending_validation_membership,
            sample_room_member_link
        )
        yield c
        close_db()


class MockRequestsResponse:
    token: str
    status_code = 200
    def json(self):
        response = {
            'id': '',
            'attributes': {
                'memberOf': [] 
            }
        }
        if self.token == TEST_HEADERS["Authorization"]:
            response['id'] = TESTING_CLIENT
            response['attributes']['memberOf'] = [
                "cn=admin,ou=groups,dc=minet,dc=net",
                "cn=treasurer,ou=groups,dc=minet,dc=net",
                "cn=network,ou=groups,dc=minet,dc=net",
                "cn=production,ou=groups,dc=minet,dc=net",
            ]
        else: 
            response['id'] = SAMPLE_CLIENT
            del response['attributes']
        return response


@pytest.fixture(autouse=True)
def mock_oidc_authentication(monkeypatch):
    from adh6.authentication import requests
    """Mock the response for our cas"""
    def mock_get(*args, **kwargs):
        r = MockRequestsResponse()
        r.token = kwargs.get("headers", {}).get("Authorization", "")
        return r
    monkeypatch.setattr(requests, "get", mock_get, raising=False)


@pytest.fixture
def account_type(faker):
    yield AccountType(
        id=faker.random_digit_not_null(),
        name="Adhérent"
    )

@pytest.fixture
def sample_account(account_type: AccountType, sample_member: Adherent):
    yield Account(
        id=1,
        type=account_type.id,
        creation_date=datetime.now(),
        name="account",
        actif=True,
        compte_courant=False,
        pinned=False,
        adherent_id=sample_member.id
    )

@pytest.fixture
def sample_account_frais_asso(account_type: AccountType):
    yield Account(
        id=2,
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
        id=3,
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
        adherent_id=sample_member.id,
        type=DeviceType.wired.value,
        ip=faker.ipv4_public(),
        ipv6=faker.ipv6(),
    )


@pytest.fixture
def wired_device2(faker, sample_member):
    yield Device(
        id=faker.random_digit_not_null(),
        mac=faker.mac_address(),
        adherent_id=sample_member.id,
        type=DeviceType.wired.value,
        ip=faker.ipv4_public(),
        ipv6=faker.ipv6(),
    )


@pytest.fixture
def wireless_device(faker, sample_member):
    yield Device(
        id=faker.random_digit_not_null(),
        mac=faker.mac_address(),
        adherent_id=sample_member.id,
        type=DeviceType.wireless.value,
        ip=faker.ipv4_private(),
        ipv6=faker.ipv6(),
    )


@pytest.fixture
def sample_vlan():
    yield Vlan(
        id=42,
        numero=42,
        adresses="192.168.42.0/24",
        adressesv6="fe80:42::0/64",
    )


@pytest.fixture
def sample_vlan69():
    yield Vlan(
        id=69,
        numero=69,
        adresses="192.168.69.0/24",
        adressesv6="fe80:69::0/64",
    )


@pytest.fixture
def sample_room1(sample_vlan):
    yield Chambre(
        id=420,
        numero=5110,
        description="Chambre de l'ambiance",
        vlan_id=sample_vlan.id,
    )


@pytest.fixture
def sample_room2(sample_vlan69):
    yield Chambre(
        id=840,
        numero=4592,
        description="Chambre voisine du swag",
        vlan_id=sample_vlan69.id,
    )


def sample_member_admin():
    return Adherent(
        id=TESTING_CLIENT_ID,
        login=TESTING_CLIENT,
        mail="test@example.com",
        nom="Test",
        prenom="test",
        password="",
        mail_membership=1,
        date_de_depart=datetime.now() - timedelta(days=1),
        subnet="10.42.0.16/28",
        ip="157.159.40.1"
    )

def api_key_user():
    from hashlib import sha3_512
    return ApiKey(
        id=1,
        user_login=TESTING_CLIENT,
        value=sha3_512(TEST_HEADERS_API_KEY_USER["X-API-KEY"].encode("utf-8")).hexdigest(),
    )


def api_key_user_roles():
    return AuthenticationRoleMapping(
        authentication=AuthenticationMethod.API_KEY,
        identifier=str(api_key_user().id),
        role=Roles.USER
    )


def api_key_admin():
    from hashlib import sha3_512
    return ApiKey(
        id=2,
        user_login=TESTING_CLIENT,
        value=sha3_512(TEST_HEADERS_API_KEY_ADMIN["X-API-KEY"].encode("utf-8")).hexdigest(),
    )


def api_key_admin_read_roles():
    return AuthenticationRoleMapping(
        authentication=AuthenticationMethod.API_KEY,
        identifier=str(api_key_admin().id),
        role=Roles.ADMIN_READ
    )


def api_key_admin_write_roles():
    return AuthenticationRoleMapping(
        authentication=AuthenticationMethod.API_KEY,
        identifier=str(api_key_admin().id),
        role=Roles.ADMIN_WRITE
    )


def oidc_admin_prod_role():
    return AuthenticationRoleMapping(
        authentication=AuthenticationMethod.OIDC,
        identifier="production",
        role=Roles.ADMIN_PROD
    )


def oidc_admin_read_role():
    return AuthenticationRoleMapping(
        authentication=AuthenticationMethod.OIDC,
        identifier="admin",
        role=Roles.ADMIN_READ
    )


def oidc_admin_write_role():
    return AuthenticationRoleMapping(
        authentication=AuthenticationMethod.OIDC,
        identifier="admin",
        role=Roles.ADMIN_WRITE
    )


def oidc_treasurer_read_role():
    return AuthenticationRoleMapping(
        authentication=AuthenticationMethod.OIDC,
        identifier="treasurer",
        role=Roles.TRESO_READ
    )


def oidc_treasurer_write_role():
    return AuthenticationRoleMapping(
        authentication=AuthenticationMethod.OIDC,
        identifier="treasurer",
        role=Roles.TRESO_WRITE
    )


def oidc_network_read_role():
    return AuthenticationRoleMapping(
        authentication=AuthenticationMethod.OIDC,
        identifier="network",
        role=Roles.NETWORK_READ
    )


def oidc_network_write_role():
    return AuthenticationRoleMapping(
        authentication=AuthenticationMethod.OIDC,
        identifier="network",
        role=Roles.NETWORK_WRITE
    )


@pytest.fixture
def sample_complete_membership(sample_account: Account, sample_member: Adherent, sample_payment_method: PaymentMethod):
    yield Membership(
        uuid=str(uuid4()),
        account_id=sample_account.id,
        create_at=datetime.now(),
        duration=MembershipDuration.ONE_YEAR,
        has_room=True,
        first_time=True,
        adherent_id=sample_member.id,
        status=MembershipStatus.COMPLETE,
        update_at=datetime.now(),
        products="[]",
        payment_method_id=sample_payment_method.id,
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
        adherent_id=sample_member2.id,
        status=MembershipStatus.PENDING_PAYMENT_VALIDATION,
        update_at=datetime.now(),
        products="[]"
    )

# Member that have an account and a membership
@pytest.fixture
def sample_member(faker, sample_room1):
    yield Adherent(
        id=SAMPLE_CLIENT_ID,
        nom='Dubois',
        prenom='Jean-Louis',
        mail='j.dubois@free.fr',
        login=SAMPLE_CLIENT,
        password='a',
        chambre_id=sample_room1.id,
        date_de_depart=tomorrow,
        datesignedminet=datetime.now(),
        ip=faker.ipv4_public(),
        subnet="10.42.172.16/28",
        mail_membership=249
    )


@pytest.fixture
def sample_member2(sample_room1):
    yield Adherent(
        id=2,
        nom='Reignier',
        prenom='Edouard',
        mail='bgdu78@hotmail.fr',
        login='reignier',
        commentaires='Desauthent pour routeur',
        password='a',
        chambre_id=sample_room1.id,
        date_de_depart=tomorrow,
        mail_membership=1,
    )


@pytest.fixture
def sample_member3(sample_room1):
    yield Adherent(
        id=3,
        nom='Dupont',
        prenom='Jean',
        mail='test@oyopmail.fr',
        login="jamaislememe",
        commentaires='abcdef',
        password='b',
        chambre_id=sample_room1.id,
        date_de_depart=tomorrow,
        mail_membership=1,
    )


@pytest.fixture
def sample_member13():
    """ Membre sans chambre """
    yield Adherent(
        id=13,
        nom='Robert',
        prenom='Dupond',
        mail='robi@hotmail.fr',
        login='dupond_r',
        commentaires='a',
        password='a',
        date_de_depart=tomorrow,
        mail_membership=1,
    )


@pytest.fixture
def sample_switch1():
    yield Switch(
        id=1,
        description="Switch sample 1",
        ip="192.168.102.51",
        communaute="GrosMotDePasse",
    )


@pytest.fixture
def sample_switch2():
    yield Switch(
        id=2,
        description="Switch sample 2",
        ip="192.168.102.52",
        communaute="GrosMotDePasse",
    )


@pytest.fixture
def sample_port1(sample_switch1, sample_room1):
    yield Port(
        rcom=1,
        numero="0/0/1",
        oid="1.1.1",
        switch_id=sample_switch1.id,
        chambre_id=sample_room1.id,
    )


@pytest.fixture
def sample_port2(sample_switch2, sample_room1):
    yield Port(
        rcom=2,
        numero="0/0/2",
        oid="1.1.2",
        switch_id=sample_switch2.id,
        chambre_id=sample_room1.id,

    )

@pytest.fixture
def sample_room_member_link(sample_room1, sample_member):
    yield RoomMemberLink(
        room_id=sample_room1.id,
        member_id=sample_member.id
    )
