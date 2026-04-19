from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.authentication.enums import AuthenticationMethod, Roles
from adh6.authentication.storage.models import AuthenticationRoleMapping
from adh6.authentication.storage.role_repository import RoleSQLRepository


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.execute = AsyncMock()
    session.scalar = AsyncMock()
    return session


@pytest.fixture
def role_repo(mock_session):
    return RoleSQLRepository(session=mock_session)


class TestRoleSQLRepository:
    async def test_get(self, role_repo, mock_session):
        # Given
        role = AuthenticationRoleMapping(
            id=1, identifier="user1", authentication=AuthenticationMethod.USER, role=Roles.USER
        )
        mock_session.scalar.return_value = role

        # When
        result = await role_repo.get(1)

        # Then
        assert result == role

    async def test_find(self, role_repo, mock_session):
        # Given
        role = AuthenticationRoleMapping(
            id=1, identifier="user1", authentication=AuthenticationMethod.USER, role=Roles.USER
        )
        mock_result = MagicMock()
        mock_result.all.return_value = [(role,)]
        mock_session.execute.return_value = mock_result

        # When
        results, count = await role_repo.find(method=AuthenticationMethod.USER)

        # Then
        assert count == 1
        assert len(results) == 1
        assert results[0].identifier == "user1"

    async def test_create(self, role_repo, mock_session):
        # Given
        # When
        await role_repo.create(AuthenticationMethod.USER, "user1", [Roles.USER])

        # Then
        mock_session.execute.assert_called_once()

    async def test_delete(self, role_repo, mock_session):
        # Given
        role = AuthenticationRoleMapping(
            id=1, identifier="user1", authentication=AuthenticationMethod.USER, role=Roles.USER
        )
        mock_session.scalar.return_value = role

        # When
        await role_repo.delete(1)

        # Then
        assert mock_session.execute.call_count >= 1

    async def test_user_id_from_username(self, role_repo, mock_session):
        # Given
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = 123
        mock_session.execute.return_value = mock_result

        # When
        result = await role_repo.user_id_from_username("user1")

        # Then
        assert result == 123
