from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from adh6.authentication.enums import AuthenticationMethod, Roles
from adh6.authentication.storage.models import ApiKey, AuthenticationRoleMapping
from adh6.constants import MembershipDuration, MembershipStatus
from adh6.device.storage.device_repository import DeviceType
from adh6.device.storage.models import Device
from adh6.member.storage.models import Adherent, Membership
from adh6.network.storage.models import Port, Switch
from adh6.room.storage.models import Chambre, RoomMemberLink
from adh6.subnet.storage.models import Vlan
from adh6.treasury.storage.models import PaymentMethod

from test import SAMPLE_CLIENT, SAMPLE_CLIENT_ID, TESTING_CLIENT, TESTING_CLIENT_ID
from test.integration.context import tomorrow
from test.integration.resource import (
    TEST_HEADERS_API_KEY_ADMIN,
    TEST_HEADERS_API_KEY_NETWORK,
    TEST_HEADERS_API_KEY_NETWORK_DEV,
    TEST_HEADERS_API_KEY_NETWORK_HOSTING,
    TEST_HEADERS_API_KEY_NETWORK_PROD,
    TEST_HEADERS_API_KEY_TRESO,
    TEST_HEADERS_API_KEY_USER,
)


@pytest.fixture(scope="session", autouse=True)
def disable_elk():
    """Always disable ELK in tests, regardless of .env settings."""
    from adh6.config.configuration import settings

    original = settings.elk_enabled
    settings.elk_enabled = False
    yield
    settings.elk_enabled = original


@pytest.fixture(scope="session")
def _app():
    """Session-scoped FastAPI app instance."""
    from .context import app

    return app


@pytest.fixture(scope="session")
async def _db_setup(_app):
    """Session-scoped database schema creation."""
    from adh6.database import engine
    from adh6.storage.sql.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="session")
def _test_client(_app, _db_setup):
    """Session-scoped TestClient instance."""
    from starlette.testclient import TestClient

    # TestClient handles async/sync internally - don't use as context manager for session scope
    client = TestClient(_app)
    yield client
    client.close()


async def add_test_fixtures(*fixtures):
    """Helper to add fixtures to database and commit."""
    from adh6.database import async_session_factory

    async with async_session_factory() as session:
        for fixture in fixtures:
            if isinstance(fixture, list):
                session.add_all(fixture)
            else:
                session.add(fixture)
        await session.commit()


async def cleanup_test_data():
    """Delete all data from all tables."""
    from adh6.database import async_session_factory, engine
    from adh6.storage.sql.models import Base
    from sqlalchemy import text

    async with async_session_factory() as session:
        # Disable foreign key checks for cleanup (MySQL/MariaDB only)
        if "mysql" in engine.url.drivername:
            await session.execute(text("SET FOREIGN_KEY_CHECKS=0"))

        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())

        # Re-enable foreign key checks
        if "mysql" in engine.url.drivername:
            await session.execute(text("SET FOREIGN_KEY_CHECKS=1"))

        await session.commit()


# Default client fixture removed - each test file defines its own client fixture
# with specific dependencies now to avoid fixture resolution conflicts


@pytest.fixture
def sample_payment_method():
    return PaymentMethod(id=1, name="liquide")


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


@pytest.fixture
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
        ip="157.159.40.1",
    )


def api_key_user():
    return ApiKey(
        id=1,
        user_login=TESTING_CLIENT,
        value=hash_api_key(TEST_HEADERS_API_KEY_USER["X-API-KEY"].encode("utf-8")),
    )


def api_key_user_roles():
    return AuthenticationRoleMapping(
        authentication=AuthenticationMethod.API_KEY,
        identifier=str(api_key_user().id),
        role=Roles.USER,
    )


def api_key_admin():
    return ApiKey(
        id=2,
        user_login=TESTING_CLIENT,
        value=hash_api_key(TEST_HEADERS_API_KEY_ADMIN["X-API-KEY"].encode("utf-8")),
    )


def api_key_admin_read_roles():
    return AuthenticationRoleMapping(
        authentication=AuthenticationMethod.API_KEY,
        identifier=str(api_key_admin().id),
        role=Roles.ADMIN_READ,
    )


def api_key_admin_write_roles():
    return AuthenticationRoleMapping(
        authentication=AuthenticationMethod.API_KEY,
        identifier=str(api_key_admin().id),
        role=Roles.ADMIN_WRITE,
    )


def api_key_admin_network_read_roles():
    return AuthenticationRoleMapping(
        authentication=AuthenticationMethod.API_KEY,
        identifier=str(api_key_admin().id),
        role=Roles.NETWORK_READ,
    )


def api_key_admin_network_write_roles():
    return AuthenticationRoleMapping(
        authentication=AuthenticationMethod.API_KEY,
        identifier=str(api_key_admin().id),
        role=Roles.NETWORK_WRITE,
    )


def api_key_treso():
    return ApiKey(
        id=3,
        user_login=TESTING_CLIENT,
        value=hash_api_key(TEST_HEADERS_API_KEY_TRESO["X-API-KEY"].encode("utf-8")),
    )


def api_key_treso_read_roles():
    return AuthenticationRoleMapping(
        authentication=AuthenticationMethod.API_KEY,
        identifier=str(api_key_treso().id),
        role=Roles.TRESO_READ,
    )


def api_key_treso_write_roles():
    return AuthenticationRoleMapping(
        authentication=AuthenticationMethod.API_KEY,
        identifier=str(api_key_treso().id),
        role=Roles.TRESO_WRITE,
    )


def api_key_network():
    return ApiKey(
        id=4,
        user_login=TESTING_CLIENT,
        value=hash_api_key(TEST_HEADERS_API_KEY_NETWORK["X-API-KEY"].encode("utf-8")),
    )


def api_key_network_read_roles():
    return AuthenticationRoleMapping(
        authentication=AuthenticationMethod.API_KEY,
        identifier=str(api_key_network().id),
        role=Roles.NETWORK_READ,
    )


def api_key_network_write_roles():
    return AuthenticationRoleMapping(
        authentication=AuthenticationMethod.API_KEY,
        identifier=str(api_key_network().id),
        role=Roles.NETWORK_WRITE,
    )


def api_key_network_dev():
    return ApiKey(
        id=5,
        user_login=TESTING_CLIENT,
        value=hash_api_key(TEST_HEADERS_API_KEY_NETWORK_DEV["X-API-KEY"].encode("utf-8")),
    )


def api_key_network_dev_roles():
    return AuthenticationRoleMapping(
        authentication=AuthenticationMethod.API_KEY,
        identifier=str(api_key_network_dev().id),
        role=Roles.NETWORK_DEV,
    )


def api_key_network_prod():
    return ApiKey(
        id=6,
        user_login=TESTING_CLIENT,
        value=hash_api_key(TEST_HEADERS_API_KEY_NETWORK_PROD["X-API-KEY"].encode("utf-8")),
    )


def api_key_network_prod_roles():
    return AuthenticationRoleMapping(
        authentication=AuthenticationMethod.API_KEY,
        identifier=str(api_key_network_prod().id),
        role=Roles.NETWORK_PROD,
    )


def api_key_network_hosting():
    return ApiKey(
        id=7,
        user_login=TESTING_CLIENT,
        value=hash_api_key(TEST_HEADERS_API_KEY_NETWORK_HOSTING["X-API-KEY"].encode("utf-8")),
    )


def api_key_network_hosting_roles():
    return AuthenticationRoleMapping(
        authentication=AuthenticationMethod.API_KEY,
        identifier=str(api_key_network_hosting().id),
        role=Roles.NETWORK_HOSTING,
    )


def hash_api_key(key: bytes) -> str:
    from hashlib import sha3_512

    return sha3_512(key).hexdigest()


def api_key_fixtures() -> list[ApiKey | AuthenticationRoleMapping]:
    return [
        api_key_user(),
        api_key_user_roles(),
        api_key_admin(),
        api_key_admin_read_roles(),
        api_key_admin_write_roles(),
        api_key_admin_network_read_roles(),
        api_key_admin_network_write_roles(),
        api_key_treso(),
        api_key_treso_read_roles(),
        api_key_treso_write_roles(),
        api_key_network(),
        api_key_network_read_roles(),
        api_key_network_write_roles(),
        api_key_network_dev(),
        api_key_network_dev_roles(),
        api_key_network_prod(),
        api_key_network_prod_roles(),
        api_key_network_hosting(),
        api_key_network_hosting_roles(),
    ]


def oidc_admin_prod_role():
    return AuthenticationRoleMapping(
        authentication=AuthenticationMethod.OIDC,
        identifier="production",
        role=Roles.ADMIN_PROD,
    )


def oidc_admin_read_role():
    return AuthenticationRoleMapping(
        authentication=AuthenticationMethod.OIDC,
        identifier="admin",
        role=Roles.ADMIN_READ,
    )


def oidc_admin_write_role():
    return AuthenticationRoleMapping(
        authentication=AuthenticationMethod.OIDC,
        identifier="admin",
        role=Roles.ADMIN_WRITE,
    )


def oidc_treasurer_read_role():
    return AuthenticationRoleMapping(
        authentication=AuthenticationMethod.OIDC,
        identifier="treasurer",
        role=Roles.TRESO_READ,
    )


def oidc_treasurer_write_role():
    return AuthenticationRoleMapping(
        authentication=AuthenticationMethod.OIDC,
        identifier="treasurer",
        role=Roles.TRESO_WRITE,
    )


def oidc_network_read_role():
    return AuthenticationRoleMapping(
        authentication=AuthenticationMethod.OIDC,
        identifier="network",
        role=Roles.NETWORK_READ,
    )


def oidc_network_write_role():
    return AuthenticationRoleMapping(
        authentication=AuthenticationMethod.OIDC,
        identifier="network",
        role=Roles.NETWORK_WRITE,
    )


@pytest.fixture
def sample_complete_membership(
    sample_member: Adherent,
    sample_payment_method: PaymentMethod,
):
    yield Membership(
        uuid=str(uuid4()),
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
def sample_pending_validation_membership(sample_member2: Adherent):
    """Membership that is not completed"""
    yield Membership(
        uuid=str(uuid4()),
        create_at=datetime.now(),
        duration=MembershipDuration.ONE_YEAR,
        has_room=True,
        first_time=True,
        adherent_id=sample_member2.id,
        status=MembershipStatus.PENDING_PAYMENT_VALIDATION,
        update_at=datetime.now(),
        products="[]",
    )


# Member that have an account and a membership
@pytest.fixture
def sample_member(faker, sample_room1):
    yield Adherent(
        id=SAMPLE_CLIENT_ID,
        nom="Dubois",
        prenom="Jean-Louis",
        mail="j.dubois@free.fr",
        login=SAMPLE_CLIENT,
        password="a",
        chambre_id=sample_room1.id,
        date_de_depart=tomorrow,
        datesignedminet=datetime.now(),
        ip=faker.ipv4_public(),
        subnet="10.42.172.16/28",
        mail_membership=249,
    )


@pytest.fixture
def sample_member2(sample_room1):
    yield Adherent(
        id=2,
        nom="Reignier",
        prenom="Edouard",
        mail="bgdu78@hotmail.fr",
        login="reignier",
        commentaires="Desauthent pour routeur",
        password="a",
        chambre_id=sample_room1.id,
        date_de_depart=tomorrow,
        mail_membership=1,
    )


@pytest.fixture
def sample_member3(sample_room1):
    yield Adherent(
        id=3,
        nom="Dupont",
        prenom="Jean",
        mail="test@oyopmail.fr",
        login="jamaislememe",
        commentaires="abcdef",
        password="b",
        chambre_id=sample_room1.id,
        date_de_depart=tomorrow,
        mail_membership=1,
    )


@pytest.fixture
def sample_member13():
    """Membre sans chambre"""
    yield Adherent(
        id=13,
        nom="Robert",
        prenom="Dupond",
        mail="robi@hotmail.fr",
        login="dupond_r",
        commentaires="a",
        password="a",
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
    yield RoomMemberLink(room_id=sample_room1.id, member_id=sample_member.id)
