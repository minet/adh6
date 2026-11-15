from ipaddress import ip_network

import pytest
from adh6.constants import dictionnary_subnet_public_ip_wireless
from adh6.device.storage.models import Device
from adh6.kea.client import KeaReservation
from adh6.kea.reservations import (
    DesiredReservation,
    Plan,
    apply_plan,
    desired_reservations,
    macs_of_members,
    plan_changes,
    wireless_subnet_id,
)
from adh6.kea.tracker import mark_mac, mark_member, normalize_mac, pop_marks
from adh6.member.storage.models import Adherent
from adh6.room.storage.models import Chambre
from adh6.storage.sql.models import Base, Routeur
from adh6.subnet.storage.models import Vlan
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


@pytest.fixture
async def sessions(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/kea.db")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
    async with factory.begin() as session:
        session.add_all(
            [
                Vlan(id=1, numero=41, adresses="157.159.41.0/24"),
                Chambre(id=10, numero=1001, vlan_id=1),
                Chambre(id=11, numero=1002, vlan_id=None),
                # In a room with a VLAN, with a wireless /28.
                Adherent(id=1, login="one", chambre_id=10, subnet="10.42.0.16/28"),
                # Without a room: nothing is reserved.
                Adherent(id=2, login="two", chambre_id=None, subnet="10.42.0.32/28"),
                # In a room without a VLAN: nothing is reserved either (like the old view).
                Adherent(id=3, login="three", chambre_id=11),
                Device(id=1, mac="AA-BB-CC-DD-EE-01", adherent_id=1, type=0, ip="157.159.41.10"),
                Device(id=2, mac="AA-BB-CC-DD-EE-02", adherent_id=1, type=1, ip="10.42.0.18"),
                Device(id=3, mac="AA-BB-CC-DD-EE-03", adherent_id=1, type=0, ip=None),
                Device(id=4, mac="AA-BB-CC-DD-EE-04", adherent_id=2, type=0, ip="157.159.41.11"),
                Device(id=5, mac="AA-BB-CC-DD-EE-05", adherent_id=3, type=0, ip="157.159.41.12"),
                # Orphan: its member was deleted, ADH6 has no cascade.
                Device(id=6, mac="AA-BB-CC-DD-EE-06", adherent_id=99, type=0, ip="157.159.41.13"),
                Routeur(id=7, mac="aa:bb:cc:dd:ee:07", adherent_id=1, ip="172.30.0.5"),
            ]
        )
    yield factory
    await engine.dispose()


def test_normalize_mac():
    assert normalize_mac("AA-BB-CC-DD-EE-FF") == "aa:bb:cc:dd:ee:ff"
    assert normalize_mac("aabb.ccdd.eeff") == "aa:bb:cc:dd:ee:ff"
    assert normalize_mac("not a mac") is None
    assert normalize_mac(None) is None


def test_wireless_subnet_ids_match_nat_wifi():
    # nat-wifi.conf (kea-dhcp repository): the id of a /28 is 999 + its rank in 10.42.0.0/16.
    subnets = dictionnary_subnet_public_ip_wireless().values()
    ids = [wireless_subnet_id(str(subnet)) for subnet in subnets]
    assert ids[0] == 1000
    assert ids[-1] == 1762
    for subnet, subnet_id in zip(subnets, ids, strict=True):
        rank = (int(ip_network(str(subnet)).network_address) - int(ip_network("10.42.0.0/16").network_address)) // 16
        assert subnet_id == 999 + rank


@pytest.mark.parametrize("subnet", [None, "", "garbage", "10.43.0.16/28", "2001:db8::/64"])
def test_wireless_subnet_id_rejects(subnet):
    assert wireless_subnet_id(subnet) is None


@pytest.mark.parametrize("subnet", ["10.42.25.224/28", "10.42.25.224", " 10.42.25.224/28 ", "10.42.25.230/28"])
def test_wireless_subnet_id_reads_the_address_like_the_old_view(subnet):
    # View: cast(substring_index(replace(subnet, '/28', ''), '.', -2)) * 16 + 4th octet DIV 16 - 1 + 1000
    assert wireless_subnet_id(subnet) == 25 * 16 + 224 // 16 - 1 + 1000


async def test_desired_reservations_follow_the_old_view(sessions):
    async with sessions() as session:
        desired = await desired_reservations(session)

    assert {(d.reservation, tuple(d.user_context.items())) for d in desired} == {
        (KeaReservation(41, "aa:bb:cc:dd:ee:01", "157.159.41.10"), (("adh6_device", 1),)),
        (KeaReservation(1000, "aa:bb:cc:dd:ee:02", "10.42.0.18"), (("adh6_device", 2),)),
        (KeaReservation(4242, "aa:bb:cc:dd:ee:07", "172.30.0.5"), (("adh6_router", 7),)),
    }


async def test_desired_reservations_filtered_by_mac(sessions):
    async with sessions() as session:
        desired = await desired_reservations(session, {"aa:bb:cc:dd:ee:02", "aa:bb:cc:dd:ee:06"})
        assert await desired_reservations(session, set()) == []

    assert [d.reservation for d in desired] == [KeaReservation(1000, "aa:bb:cc:dd:ee:02", "10.42.0.18")]


async def test_macs_of_a_deleted_member_are_still_found(sessions):
    async with sessions() as session:
        assert await macs_of_members(session, {99}) == {"aa:bb:cc:dd:ee:06"}
        assert await macs_of_members(session, {1}) == {
            "aa:bb:cc:dd:ee:01",
            "aa:bb:cc:dd:ee:02",
            "aa:bb:cc:dd:ee:03",
            "aa:bb:cc:dd:ee:07",
        }
        assert await macs_of_members(session, set()) == set()


async def test_marks_are_collected_then_cleared(sessions):
    async with sessions() as session:
        mark_member(session, 1)
        mark_member(session, None)
        mark_mac(session, "AA-BB-CC-DD-EE-06")
        mark_mac(session, "bad")
        assert pop_marks(session) == ({1}, {"aa:bb:cc:dd:ee:06"})
        assert pop_marks(session) == (set(), set())


def desired(subnet_id: int, mac: str, ip: str) -> DesiredReservation:
    return DesiredReservation(KeaReservation(subnet_id, mac, ip), {})


def test_plan_changes():
    current = [
        KeaReservation(41, "aa:00:00:00:00:01", "157.159.41.10"),  # unchanged
        KeaReservation(41, "aa:00:00:00:00:02", "157.159.41.11"),  # IP changed
        KeaReservation(1000, "aa:00:00:00:00:03", "10.42.0.18"),  # no longer wanted
    ]
    wanted = [
        desired(41, "aa:00:00:00:00:01", "157.159.41.10"),
        desired(41, "aa:00:00:00:00:02", "157.159.41.20"),
        desired(1001, "aa:00:00:00:00:03", "10.42.0.34"),  # moved to another /28
        desired(41, "aa:00:00:00:00:04", "157.159.41.30"),
        desired(41, "aa:00:00:00:00:04", "157.159.41.31"),  # same MAC twice in a subnet
    ]

    plan = plan_changes(current, wanted)

    assert plan.deletions == [current[1], current[2]]
    assert [a.reservation for a in plan.additions] == [
        KeaReservation(41, "aa:00:00:00:00:02", "157.159.41.20"),
        KeaReservation(1001, "aa:00:00:00:00:03", "10.42.0.34"),
        KeaReservation(41, "aa:00:00:00:00:04", "157.159.41.30"),
    ]
    assert plan.duplicates == [KeaReservation(41, "aa:00:00:00:00:04", "157.159.41.31")]


class FakeClient:
    def __init__(self, refuse: frozenset[str] = frozenset()):
        self.calls: list[tuple[str, int, str]] = []
        self.refuse = refuse

    async def delete(self, subnet_id: int, mac: str) -> bool:
        self.calls.append(("del", subnet_id, mac))
        return True

    async def add(self, reservation: KeaReservation, user_context=None) -> None:
        from adh6.kea.client import KeaError

        self.calls.append(("add", reservation.subnet_id, reservation.mac))
        if reservation.mac in self.refuse:
            raise KeaError("refused")


async def test_apply_plan_deletes_before_adding_and_counts_failures():
    client = FakeClient(refuse=frozenset({"aa:00:00:00:00:09"}))
    plan = Plan(
        deletions=[KeaReservation(41, "aa:00:00:00:00:01", "157.159.41.10")],
        additions=[desired(41, "aa:00:00:00:00:02", "157.159.41.10"), desired(41, "aa:00:00:00:00:09", "157.159.41.9")],
        duplicates=[],
    )

    report = await apply_plan(client, plan)  # type: ignore[arg-type]

    assert client.calls == [
        ("del", 41, "aa:00:00:00:00:01"),
        ("add", 41, "aa:00:00:00:00:02"),
        ("add", 41, "aa:00:00:00:00:09"),
    ]
    assert (report.deleted, report.added, report.failed) == (1, 1, 1)


async def test_apply_plan_dry_run_changes_nothing():
    client = FakeClient()
    plan = Plan(
        deletions=[KeaReservation(41, "aa:00:00:00:00:01", "157.159.41.10")],
        additions=[desired(41, "aa:00:00:00:00:02", "157.159.41.11")],
        duplicates=[],
    )

    report = await apply_plan(client, plan, dry_run=True)  # type: ignore[arg-type]

    assert client.calls == []
    assert report.changes == 2
