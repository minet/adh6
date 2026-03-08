from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from adh6.authentication import AuthenticationMethod, Roles
from adh6.authentication.storage.models import ApiKey, AuthenticationRoleMapping
from adh6.constants import MembershipDuration, MembershipStatus
from adh6.device.storage.device_repository import DeviceType
from adh6.device.storage.models import Device
from adh6.member.storage.models import Adherent, Membership
from adh6.network.storage.models import Port, Switch
from adh6.room.storage.models import Chambre, RoomMemberLink
from adh6.subnet.storage.models import Vlan
from adh6.treasury.storage.models import Account, AccountType, PaymentMethod

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

# Module-level sync engine cache
_sync_engine = None
_sync_session_factory = None


def _get_or_create_sync_engine():
    """Get or create the sync engine (cached at module level)."""
    global _sync_engine, _sync_session_factory

    if _sync_engine is None:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from adh6.config.configuration import settings

        # Convert async database URL to sync
        def to_sync_url(url: str) -> str:
            if url.startswith("mysql+aiomysql://"):
                return url.replace("mysql+aiomysql://", "mysql+mysqldb://", 1)
            if url.startswith("sqlite+aiosqlite://"):
                return url.replace("sqlite+aiosqlite://", "sqlite://", 1)
            return url

        # Create sync engine and session factory ONCE
        _sync_engine = create_engine(
            to_sync_url(settings.database_url),
            future=True,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        _sync_session_factory = sessionmaker(
            bind=_sync_engine, autoflush=False, autocommit=False, expire_on_commit=False
        )

    return _sync_engine, _sync_session_factory


@pytest.fixture(scope="session")
def _app():
    """Session-scoped FastAPI app instance."""
    from .context import app

    return app


@pytest.fixture(scope="session")
def _db_setup(_app):
    """Session-scoped database schema creation."""
    from adh6.storage.sql.models import Base

    # Use sync engine to create schema (avoids event loop conflicts with TestClient)
    sync_engine, _ = _get_or_create_sync_engine()
    Base.metadata.create_all(bind=sync_engine)

    yield

    # Clean up at end of session
    Base.metadata.drop_all(bind=sync_engine)
    sync_engine.dispose()


@pytest.fixture(scope="session")
def _test_client(_app, _db_setup):
    """Session-scoped TestClient instance."""
    from starlette.testclient import TestClient

    # TestClient handles async/sync internally - don't use as context manager for session scope
    client = TestClient(_app)
    yield client
    client.close()


def get_sync_session():
    """Create a sync session for test data setup."""
    _, session_factory = _get_or_create_sync_engine()
    return session_factory()


def add_test_fixtures(*fixtures):
    """Helper to add fixtures to database and commit."""
    session = get_sync_session()
    try:
        for fixture in fixtures:
            if isinstance(fixture, list):
                session.add_all(fixture)
            else:
                session.add(fixture)
        session.commit()
    finally:
        session.close()


def cleanup_test_data():
    """Delete all data from all tables."""
    from adh6.storage.sql.models import Base
    from sqlalchemy import text

    session = get_sync_session()
    try:
        # Disable foreign key checks for cleanup (MySQL/MariaDB only)
        if "mysql" in session.bind.url.drivername:
            session.execute(text("SET FOREIGN_KEY_CHECKS=0"))

        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())

        # Re-enable foreign key checks
        if "mysql" in session.bind.url.drivername:
            session.execute(text("SET FOREIGN_KEY_CHECKS=1"))

        session.commit()
    finally:
        session.close()


# Default client fixture removed - each test file defines its own client fixture
# with specific dependencies now to avoid fixture resolution conflicts


@pytest.fixture
def account_type(faker):
    yield AccountType(id=faker.random_digit_not_null(), name="Adhérent")


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
        adherent_id=sample_member.id,
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
        pinned=True,
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
        pinned=True,
    )


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
        value=hash_api_key(
            TEST_HEADERS_API_KEY_NETWORK_DEV["X-API-KEY"].encode("utf-8")
        ),
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
        value=hash_api_key(
            TEST_HEADERS_API_KEY_NETWORK_PROD["X-API-KEY"].encode("utf-8")
        ),
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
        value=hash_api_key(
            TEST_HEADERS_API_KEY_NETWORK_HOSTING["X-API-KEY"].encode("utf-8")
        ),
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
    sample_account: Account,
    sample_member: Adherent,
    sample_payment_method: PaymentMethod,
):
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
def sample_pending_validation_membership(
    sample_account: Account, sample_member2: Adherent
):
    """Membership that is not completed"""
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
