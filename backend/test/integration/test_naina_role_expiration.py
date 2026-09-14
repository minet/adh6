from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.authentication.enums import AuthenticationMethod, Roles
from adh6.authentication.storage import role_repository as role_repository_module
from adh6.authentication.storage.models import AuthenticationRoleMapping
from adh6.authentication.storage.role_repository import RoleSQLRepository
from adh6.member.interfaces import MemberRepository
from adh6.naina import manager as naina_manager_module
from adh6.naina.manager import NainaManager
from adh6.naina.storage import NainaSQLRepository
from sqlalchemy import Table, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


@pytest.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite://")
    async with engine.begin() as connection:
        role_mapping_table = AuthenticationRoleMapping.__table__
        assert isinstance(role_mapping_table, Table)
        await connection.run_sync(role_mapping_table.create)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as database_session:
        yield database_session

    await engine.dispose()


@pytest.fixture
def manager(session):
    member_repository = MagicMock(spec=MemberRepository)
    member_repository.get_by_login = AsyncMock(return_value=object())
    return NainaManager(NainaSQLRepository(session), member_repository)


async def test_naina_roles_are_hidden_after_their_expiration(manager, monkeypatch):
    before_cutoff = datetime(2026, 9, 14, 12, tzinfo=UTC)
    monkeypatch.setattr(naina_manager_module, "_utc_now", lambda: before_cutoff)
    await manager.create(identifier="temporary-admin")

    nainas = await manager.search()

    assert [(naina.login, naina.expires_at) for naina in nainas] == [
        ("temporary-admin", datetime(2026, 9, 14, 18, 30, tzinfo=UTC))
    ]

    after_cutoff = datetime(2026, 9, 14, 18, 30, tzinfo=UTC)
    monkeypatch.setattr(naina_manager_module, "_utc_now", lambda: after_cutoff)

    assert await manager.search() == []


async def test_creating_a_naina_purges_expired_grants(session, manager, monkeypatch):
    before_cutoff = datetime(2026, 9, 14, 12, tzinfo=UTC)
    monkeypatch.setattr(naina_manager_module, "_utc_now", lambda: before_cutoff)
    await manager.create(identifier="temporary-admin")

    next_day = datetime(2026, 9, 15, 12, tzinfo=UTC)
    monkeypatch.setattr(naina_manager_module, "_utc_now", lambda: next_day)
    await manager.create(identifier="other-admin")

    mappings = (await session.scalars(select(AuthenticationRoleMapping))).all()
    assert {mapping.identifier for mapping in mappings} == {"other-admin"}


async def test_expired_naina_roles_are_excluded_from_authentication(session, manager, monkeypatch):
    before_cutoff = datetime(2026, 9, 14, 12, tzinfo=UTC)
    monkeypatch.setattr(naina_manager_module, "_utc_now", lambda: before_cutoff)
    await manager.create(identifier="temporary-admin")

    after_cutoff = datetime(2026, 9, 14, 18, 30)
    monkeypatch.setattr(role_repository_module, "_naive_utc_now", lambda: after_cutoff)

    roles = await RoleSQLRepository(session).find_for_oidc_identity(groups=[], username="temporary-admin")

    assert roles == []


async def test_recreating_a_naina_replaces_the_existing_temporary_roles(session, manager, monkeypatch):
    now = datetime(2026, 9, 14, 12, tzinfo=UTC)
    monkeypatch.setattr(naina_manager_module, "_utc_now", lambda: now)

    await manager.create(identifier="temporary-admin")
    await manager.create(identifier="temporary-admin")

    mappings = (await session.scalars(select(AuthenticationRoleMapping))).all()
    assert len(mappings) == 4


async def test_revoking_a_naina_keeps_permanent_roles(session, manager, monkeypatch):
    now = datetime(2026, 9, 14, 12, tzinfo=UTC)
    monkeypatch.setattr(naina_manager_module, "_utc_now", lambda: now)
    repository = RoleSQLRepository(session)
    await repository.create(AuthenticationMethod.USER, "temporary-admin", [Roles.TRESO_READ])
    await manager.create(identifier="temporary-admin")

    await manager.revoke("temporary-admin")

    mappings = (await session.scalars(select(AuthenticationRoleMapping))).all()
    assert [mapping.role for mapping in mappings] == [Roles.TRESO_READ]


async def test_permanent_oidc_roles_do_not_expire(session, monkeypatch):
    repository = RoleSQLRepository(session)
    await repository.create(AuthenticationMethod.OIDC, "network-team", [Roles.NETWORK_READ])

    much_later = datetime(2036, 9, 14, 12)
    monkeypatch.setattr(role_repository_module, "_naive_utc_now", lambda: much_later)

    roles = await repository.find_for_oidc_identity(groups=["network-team"], username=None)

    assert [role.role for role in roles] == [Roles.NETWORK_READ.value]


async def test_direct_user_role_is_not_treated_as_a_naina(session, monkeypatch):
    repository = RoleSQLRepository(session)
    await repository.create(AuthenticationMethod.USER, "temporary-admin", [Roles.ADMIN_READ])

    much_later = datetime(2036, 9, 14, 12)
    monkeypatch.setattr(role_repository_module, "_naive_utc_now", lambda: much_later)

    roles = await repository.find_for_oidc_identity(groups=[], username="temporary-admin")

    assert [role.role for role in roles] == [Roles.ADMIN_READ.value]
