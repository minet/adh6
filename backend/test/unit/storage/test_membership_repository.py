import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.constants import MembershipStatus
from adh6.datetime_utils import utc_now_naive
from adh6.entity import AbstractMembership
from adh6.exceptions import MembershipNotFoundError
from adh6.member.storage.membership_repository import MembershipSQLRepository
from adh6.member.storage.models import Membership as MembershipSQL


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.flush = AsyncMock()
    session.delete = AsyncMock()
    return session


@pytest.fixture
def membership_repo(mock_session):
    return MembershipSQLRepository(session=mock_session)


class TestMembershipSQLRepository:
    async def test_search_basic(self, membership_repo, mock_session):
        # Given
        m_sql = MembershipSQL(
            uuid=str(uuid.uuid4()),
            status=MembershipStatus.COMPLETE,
            adherent_id=1,
            duration=12,
            has_room=True,
            first_time=True,
            payment_method_id=1,
            create_at=utc_now_naive(),
        )
        mock_execute_result = MagicMock()
        mock_execute_result.scalars.return_value.all.return_value = [m_sql]
        mock_session.execute = AsyncMock(return_value=mock_execute_result)
        mock_session.scalar = AsyncMock(return_value=1)

        # When
        results, count = await membership_repo.search_by()

        # Then
        assert count == 1
        assert len(results) == 1
        assert results[0].status == MembershipStatus.COMPLETE.value

    async def test_create(self, membership_repo, mock_session):
        # Given
        membership = AbstractMembership(
            member=1,
            duration=12,
            paymentMethod=1,
            status=MembershipStatus.COMPLETE.value,
        )
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 0
        mock_session.execute = AsyncMock(return_value=mock_count_result)

        # When
        result = await membership_repo.create(membership)

        # Then
        assert result.first_time is True
        mock_session.add.assert_called()
        mock_session.flush.assert_called()

    async def test_update_happy_path(self, membership_repo, mock_session):
        # Given
        u = str(uuid.uuid4())
        m_sql = MembershipSQL(
            uuid=u,
            status=MembershipStatus.PENDING_RULES,
            adherent_id=1,
            duration=12,
            has_room=True,
            first_time=True,
            payment_method_id=1,
            create_at=utc_now_naive(),
        )
        mock_session.scalar = AsyncMock(return_value=m_sql)
        membership = AbstractMembership(uuid=u, duration=6, status=MembershipStatus.COMPLETE.value)

        # When
        result = await membership_repo.update(membership)

        # Then
        assert m_sql.status == MembershipStatus.COMPLETE
        assert m_sql.duration == 6
        assert result.status == MembershipStatus.COMPLETE.value

    async def test_get_by_id(self, membership_repo, mock_session):
        u = str(uuid.uuid4())
        mock_session.scalar = AsyncMock(
            return_value=MembershipSQL(
                uuid=u,
                status=MembershipStatus.COMPLETE,
                adherent_id=1,
                duration=12,
                has_room=True,
                first_time=True,
                create_at=utc_now_naive(),
            )
        )

        result = await membership_repo.get_by_id(u)

        assert result is not None
        assert result.uuid == u

    async def test_delete(self, membership_repo, mock_session):
        u = str(uuid.uuid4())
        membership = MembershipSQL(
            uuid=u,
            status=MembershipStatus.COMPLETE,
            adherent_id=1,
            duration=12,
            has_room=True,
            first_time=True,
            create_at=utc_now_naive(),
        )
        mock_session.scalar = AsyncMock(return_value=membership)

        result = await membership_repo.delete(u)

        assert result.uuid == u
        mock_session.delete.assert_awaited_once_with(membership)

    async def test_delete_unknown_membership(self, membership_repo, mock_session):
        mock_session.scalar = AsyncMock(return_value=None)

        with pytest.raises(MembershipNotFoundError):
            await membership_repo.delete(str(uuid.uuid4()))

    async def test_validate(self, membership_repo, mock_session):
        # Given
        u = str(uuid.uuid4())
        m_sql = MembershipSQL(uuid=u, status=MembershipStatus.PENDING_PAYMENT)
        mock_session.scalar = AsyncMock(return_value=m_sql)

        # When
        await membership_repo.validate(u)

        # Then
        assert m_sql.status == MembershipStatus.COMPLETE
