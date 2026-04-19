from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.entity import AbstractMember, MemberFilter
from adh6.member.storage.member_repository import MemberSQLRepository
from adh6.member.storage.models import Adherent


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.flush = AsyncMock()
    session.delete = AsyncMock()
    session.add = MagicMock()  # .add is usually sync in SA
    return session


@pytest.fixture
def member_repo(mock_session):
    return MemberSQLRepository(session=mock_session)


class TestMemberSQLRepository:
    async def test_get_by_id(self, member_repo, mock_session):
        # Given
        adh = Adherent(id=1, login="testuser", prenom="Test", nom="User")
        mock_session.scalar = AsyncMock(return_value=adh)

        # When
        result = await member_repo.get_by_id(1)

        # Then
        assert result.id == 1
        assert result.username == "testuser"
        mock_session.scalar.assert_called_once()

    async def test_get_by_login(self, member_repo, mock_session):
        # Given
        adh = Adherent(id=1, login="testuser")
        mock_session.scalar = AsyncMock(return_value=adh)

        # When
        result = await member_repo.get_by_login("testuser")

        # Then
        assert result.username == "testuser"

    async def test_search_by_basic(self, member_repo, mock_session):
        # Given
        adh = Adherent(id=1, login="testuser")
        mock_execute_result = MagicMock()
        mock_execute_result.all.return_value = [adh]
        mock_execute_result.scalars.return_value.all.return_value = [adh]
        mock_session.execute = AsyncMock(return_value=mock_execute_result)

        # When
        results, count = await member_repo.search_by(limit=10, offset=0)

        # Then
        assert count == 1
        assert len(results) == 1
        assert results[0].username == "testuser"

    async def test_search_by_with_filter(self, member_repo, mock_session):
        # Given
        filter_ = MemberFilter(ip="127.0.0.1", since=datetime(2023, 1, 1))
        mock_execute_result = MagicMock()
        mock_execute_result.all.return_value = []
        mock_execute_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_execute_result)

        # When
        await member_repo.search_by(limit=10, offset=0, filter_=filter_)

        # Then
        mock_session.execute.assert_called()

    async def test_update_comment(self, member_repo, mock_session):
        # Given
        adh = Adherent(id=1, commentaires="Old comment")
        mock_session.scalar = AsyncMock(return_value=adh)

        # When
        await member_repo.update_comment(1, "New comment")

        # Then
        assert adh.commentaires == "New comment"

    async def test_update_password(self, member_repo, mock_session):
        # Given
        adh = Adherent(id=1, password="old")
        mock_session.scalar = AsyncMock(return_value=adh)

        # When
        await member_repo.update_password(1, "new_hashed")

        # Then
        assert adh.password == "new_hashed"

    async def test_used_wireless_public_ips(self, member_repo, mock_session):
        # Given
        mock_execute_result = MagicMock()
        mock_execute_result.all.return_value = [("1.1.1.1",), ("2.2.2.2",)]
        mock_session.execute = AsyncMock(return_value=mock_execute_result)

        # When
        ips = await member_repo.used_wireless_public_ips()

        # Then
        assert len(ips) == 2
        assert str(ips[0]) == "1.1.1.1"

    async def test_add_duration(self, member_repo, mock_session):
        # Given
        initial_date = date(2023, 1, 1)
        adh = Adherent(id=1, date_de_depart=initial_date)
        mock_session.scalar = AsyncMock(return_value=adh)

        # When
        await member_repo.add_duration(1, 1)  # Add 1 month

        # Then
        assert adh.date_de_depart is not None
        assert adh.date_de_depart > initial_date

    async def test_update_happy_path(self, member_repo, mock_session):
        # Given
        adh = Adherent(id=1, login="old", prenom="Old", nom="Old", mail="old@example.com")
        mock_session.scalar = AsyncMock(return_value=adh)
        abstract = AbstractMember(id=1, username="new", firstName="New", lastName="New", email="new@example.com")

        # When
        result = await member_repo.update(abstract, override=True)

        # Then
        assert result.username == "new"
        assert adh.login == "new"
        mock_session.flush.assert_called()

    async def test_delete_happy_path(self, member_repo, mock_session):
        # Given
        adh = Adherent(id=1, login="testuser")
        mock_session.scalar = AsyncMock(return_value=adh)

        # When
        await member_repo.delete(1)

        # Then
        mock_session.delete.assert_called_once_with(adh)
