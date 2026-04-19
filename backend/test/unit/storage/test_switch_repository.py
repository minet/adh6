from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.entity import AbstractSwitch, Switch
from adh6.network.storage.models import Switch as SQLSwitch
from adh6.network.storage.switch_repository import SwitchSQLRepository


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.execute = AsyncMock()
    session.flush = AsyncMock()
    session.scalar = AsyncMock()
    session.delete = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def switch_repo(mock_session):
    return SwitchSQLRepository(session=mock_session)


class TestSwitchSQLRepository:
    async def test_get_by_id(self, switch_repo, mock_session):
        # Given
        sql_sw = SQLSwitch(id=1, description="SW1", ip="10.0.0.1")
        mock_session.scalar.return_value = sql_sw

        # When
        result = await switch_repo.get_by_id(1)

        # Then
        assert result.id == 1
        assert result.description == "SW1"

    async def test_search_by(self, switch_repo, mock_session):
        # Given
        sql_sw = SQLSwitch(id=1, description="SW1", ip="10.0.0.1")
        mock_execute_result = MagicMock()
        mock_execute_result.all.return_value = [sql_sw]
        mock_execute_result.scalars.return_value.all.return_value = [sql_sw]
        mock_session.execute.return_value = mock_execute_result

        # When
        results, count = await switch_repo.search_by(terms="SW1")

        # Then
        assert count == 1
        assert len(results) == 1

    async def test_create(self, switch_repo, mock_session):
        # Given
        sw = Switch(id=None, description="New SW", ip="10.0.0.2")

        # When
        _ = await switch_repo.create(sw)

        # Then
        mock_session.add.assert_called()
        mock_session.flush.assert_called()

    async def test_update(self, switch_repo, mock_session):
        # Given
        sql_sw = SQLSwitch(id=1, description="Old", ip="10.0.0.1")
        mock_session.scalar.return_value = sql_sw
        update_info = AbstractSwitch(id=1, description="New")

        # When
        _ = await switch_repo.update(update_info)

        # Then
        assert sql_sw.description == "New"
        mock_session.flush.assert_called()

    async def test_delete(self, switch_repo, mock_session):
        # Given
        sql_sw = SQLSwitch(id=1)
        mock_session.scalar.return_value = sql_sw

        # When
        await switch_repo.delete(1)

        # Then
        mock_session.delete.assert_called_once_with(sql_sw)
