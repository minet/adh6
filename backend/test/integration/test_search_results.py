import pytest
from adh6.device.storage.device_repository import DeviceSQLRepository
from adh6.device.storage.models import Device
from adh6.entity import AbstractPort, DeviceFilter, MemberFilter
from adh6.member.storage.member_repository import MemberSQLRepository
from adh6.member.storage.models import Adherent, Membership
from adh6.network.storage.models import Port, Switch
from adh6.network.storage.port_repository import PortSQLRepository
from adh6.network.storage.switch_repository import SwitchSQLRepository
from adh6.room.storage.models import Chambre
from adh6.room.storage.room_repository import RoomSQLRepository
from adh6.storage import Base
from adh6.subnet.storage.models import Vlan
from adh6.treasury.storage.models import PaymentMethod, Product, Transaction
from adh6.treasury.storage.payment_method_repository import PaymentMethodSQLRepository
from adh6.treasury.storage.product_repository import ProductSQLRepository
from adh6.treasury.storage.transaction_repository import TransactionSQLRepository
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


@pytest.fixture
async def search_session():
    engine = create_async_engine("sqlite+aiosqlite://")
    tables = [
        model.__table__
        for model in [Adherent, Membership, Vlan, Chambre, Switch, Port, Device, PaymentMethod, Product, Transaction]
    ]
    async with engine.begin() as connection:
        await connection.run_sync(lambda connection: Base.metadata.create_all(connection, tables=tables))
    async with async_sessionmaker(engine, expire_on_commit=False)() as session:
        session.add_all(
            [
                Adherent(id=1, login="jdupont", prenom="Jean Pierre", nom="Dupont", mail="jean@example.org"),
                Adherent(id=2, login="literal_user", prenom="Literal", nom="User"),
                Membership(uuid="first", adherent_id=1, status="COMPLETE"),
                Membership(uuid="second", adherent_id=1, status="COMPLETE"),
                Chambre(id=42, numero=5110, description="Chambre DOUBLE"),
                Switch(id=7, description="Bâtiment NORD", ip="192.0.2.7"),
                Port(id=1, numero="Gi1/0/1", oid="1.1", chambre_id=42, switch_id=7),
                Port(id=2, numero="Gi1/0/2", oid="1.2", switch_id=7),
                Device(id=1, adherent_id=1, mac="aa:bb:cc:dd:ee:ff", name="Portable", type=0, ipv6="::1"),
                Device(id=2, adherent_id=999, mac="11:22:33:44:55:66", name="Orphan", type=0, ipv6="2001:db8::2"),
                Product(id=1, name="Cotisation", buying_price=0, selling_price=100),
                Product(id=2, name="Literal_100%", buying_price=0, selling_price=100),
                PaymentMethod(id=1, name="Espèces"),
                PaymentMethod(id=2, name="Literal_100%"),
                Transaction(id=1, name="Cotisation", value=100, type=1, author_id=1),
                Transaction(id=2, name="Literal_100%", value=100, type=1, author_id=1),
            ]
        )
        await session.flush()
        yield session
    await engine.dispose()


@pytest.mark.parametrize("terms", [" Jean   Pierre Dupont ", "dupont jean pierre", "JEAN@example.org"])
async def test_member_search_handles_spaces_compound_names_and_email(search_session, terms):
    members, count = await MemberSQLRepository(search_session).search_by(10, 0, terms)
    assert [member.id for member in members] == [1]
    assert count == 1


async def test_membership_filter_returns_each_member_once(search_session):
    members, count = await MemberSQLRepository(search_session).search_by(
        10, 0, "dupont", MemberFilter(membership="COMPLETE")
    )
    assert [member.id for member in members] == [1]
    assert count == 1


@pytest.mark.parametrize(
    "terms, expected",
    [
        ("portable", [1]),
        ("AABB.CCDD.EEFF", [1]),
        ("11-22-33-44-55-66", [2]),
        (" JDUPONT ", [1]),
        ("::1", [1]),
        ("::2", [2]),
        ("2001:db8::2", [2]),
        ("-", [1, 2]),
    ],
)
async def test_device_search_finds_names_mac_formats_and_devices_without_an_owner(search_session, terms, expected):
    devices, count = await DeviceSQLRepository(search_session).search_by(10, 0, DeviceFilter(terms=terms))
    assert [device.id for device in devices] == expected
    assert count == len(expected)


@pytest.mark.parametrize("terms, expected", [("511", [1]), (" nord ", [1, 2]), ("192.0.2.7", [1, 2]), ("gi1/0/2", [2])])
async def test_port_search_finds_displayed_fields_and_combines_filters(search_session, terms, expected):
    ports, count = await PortSQLRepository(search_session).search_by(terms=terms, filter_=AbstractPort(switchObj=7))
    assert {port.id for port in ports} == set(expected)
    assert len(ports) == count == len(expected)


@pytest.mark.parametrize(
    "repository, terms, expected",
    [
        (MemberSQLRepository, "_", [2]),
        (ProductSQLRepository, "%", [2]),
        (PaymentMethodSQLRepository, "%", [2]),
        (TransactionSQLRepository, "_", [2]),
        (RoomSQLRepository, "%", []),
        (SwitchSQLRepository, "%", []),
        (PortSQLRepository, "%", []),
    ],
)
async def test_search_treats_sql_wildcards_as_literal_text(search_session, repository, terms, expected):
    results, count = await repository(search_session).search_by(limit=10, offset=0, terms=terms)
    assert [result.id for result in results] == expected
    assert count == len(expected)


@pytest.mark.parametrize(
    "repository, terms",
    [
        (RoomSQLRepository, " DOUBLE "),
        (SwitchSQLRepository, " nord "),
        (ProductSQLRepository, " COTISATION "),
        (PaymentMethodSQLRepository, " ESPèCES "),
        (TransactionSQLRepository, " COTISATION "),
    ],
)
async def test_text_search_is_case_insensitive_and_trims_spaces(search_session, repository, terms):
    results, count = await repository(search_session).search_by(limit=10, offset=0, terms=terms)
    assert len(results) == count == 1


async def test_port_room_and_switch_filters_use_database_ids_and_intersect_text(search_session):
    repository = PortSQLRepository(search_session)
    filters = AbstractPort(room=42, switchObj=7)
    ports, count = await repository.search_by(terms="nord", filter_=filters)
    assert [port.id for port in ports] == [1]
    assert count == 1
    ports, count = await repository.search_by(terms="Gi1/0/2", filter_=filters)
    assert ports == []
    assert count == 0


@pytest.mark.parametrize(
    "repository, expected",
    [
        (MemberSQLRepository, 2),
        (PortSQLRepository, 2),
        (RoomSQLRepository, 1),
        (SwitchSQLRepository, 1),
        (ProductSQLRepository, 2),
        (TransactionSQLRepository, 2),
        (PaymentMethodSQLRepository, 2),
    ],
)
async def test_empty_or_whitespace_search_restores_all_results(search_session, repository, expected):
    results, count = await repository(search_session).search_by(limit=10, offset=0, terms="   ")
    assert len(results) == count == expected


async def test_room_search_loads_vlans_in_bulk_instead_of_one_query_per_result(search_session):
    search_session.add(Vlan(id=1, numero=101))
    search_session.add_all([Chambre(numero=6000 + index, vlan_id=1) for index in range(10)])
    await search_session.flush()
    search_session.expunge_all()
    statements = []
    engine = search_session.bind.sync_engine

    def record_statement(connection, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    event.listen(engine, "before_cursor_execute", record_statement)
    try:
        rooms, count = await RoomSQLRepository(search_session).search_by(limit=10, terms="60")
    finally:
        event.remove(engine, "before_cursor_execute", record_statement)

    assert len(rooms) == count == 10
    assert all(room.vlan == 101 for room in rooms)
    assert len(statements) <= 3
