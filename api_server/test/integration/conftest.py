import datetime
import pytest

from config.TEST_CONFIGURATION import DATABASE
from src.interface_adapter.http_api.auth import TESTING_CLIENT
from src.interface_adapter.sql.model.database import Database as db
from src.interface_adapter.sql.model.models import (
    Adherent, Admin, Chambre, Vlan, Device, Switch, Port)
from test.integration.test_member import prep_db


@pytest.fixture
def wired_device(faker, sample_member1):
    yield Device(
        id=faker.random_digit_not_null,
        mac=faker.mac_address,
        adherent=sample_member1,
        type='wired',
        ip=faker.ipv4_public(network='157.159.41.0/24'),
        ipv6=faker.ipv6,
    )


@pytest.fixture
def wired_device2(faker, sample_member3):
    yield Device(
        id=faker.random_digit_not_null,
        mac=faker.mac_address,
        adherent=sample_member3,
        type='wired',
        ip=faker.ipv4_public(network='157.159.41.0/24'),
        ipv6=faker.ipv6,
    )


@pytest.fixture
def wireless_device(faker, sample_member2):
    yield Device(
        id=faker.random_digit_not_null,
        mac=faker.mac_address,
        adherent=sample_member2,
        type='wireless',
        ip=faker.ipv4_public(network='157.159.41.0/24'),
        ipv6=faker.ipv6,
    )


@pytest.fixture
def wireless_device_dict():
    '''
    Device that will be inserted/updated when tests are run.
    It is not present in the api_client by default
    '''
    yield {
        'mac': '01-23-45-67-89-AC',
        'connectionType': 'wireless',
        'type': 'wireless',
        'username': 'dubois_j'
    }


@pytest.fixture
def wired_device_dict():
    yield {
        'mac': '01-23-45-67-89-AD',
        'ipAddress': '127.0.0.1',
        'ipv6Address': 'dbb1:39b7:1e8f:1a2a:3737:9721:5d16:166',
        'connectionType': 'wired',
        'type': 'wired',
        'username': 'dupontje'
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


@pytest.fixture
def sample_admin():
    yield Admin(
        roles=""
    )

@pytest.fixture
def sample_member_admin(sample_admin):
    yield Adherent(
                login=TESTING_CLIENT,
                mail="test@example.com",
                nom="Test",
                prenom="test",
                password="",
                admin=sample_admin
            )


@pytest.fixture
def sample_member1(sample_room1):
    yield Adherent(
        nom='Dubois',
        prenom='Jean-Louis',
        mail='j.dubois@free.fr',
        login='dubois_j',
        password='a',
        chambre=sample_room1,
        date_de_depart=datetime.datetime(2005, 7, 14, 12, 30).date(),
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
    )


@pytest.fixture
def sample_member3(sample_room1):
    yield Adherent(
        nom='Dupont',
        prenom='Jean',
        mail='test@oyopmail.fr',
        login='dupontje',
        commentaires='abcdef',
        password='b',
        chambre=sample_room1,
        date_de_depart=datetime.datetime(2105, 7, 14, 12, 30).date(),
    )


@pytest.fixture
def sample_member13(sample_room2):
    """ Membre sans chambre """
    yield Adherent(
        nom='Robert',
        prenom='Dupond',
        mail='robi@hotmail.fr',
        login='dupond_r',
        commentaires='a',
        password='a',
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
        chambre_id=0,

    )


@pytest.fixture
def sample_port2(sample_switch2):
    yield Port(
        rcom=2,
        numero="0/0/2",
        oid="1.1.2",
        switch=sample_switch2,
        chambre_id=0,

    )


@pytest.fixture
def api_client(sample_member1, sample_member2, sample_member13,
               wired_device, wireless_device,
               sample_room1, sample_room2, sample_vlan):
    from .context import app
    with app.app.test_client() as c:
        db.init_db(DATABASE, testing=True)
        prep_db(db.get_db().get_session(),
                sample_member1,
                sample_member2,
                sample_member13,
                wired_device,
                wireless_device,
                sample_room1,
                sample_room2,
                sample_vlan)
        yield c


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
