import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.constants import MembershipStatus
from adh6.entity import SubscriptionBody
from adh6.member.storage.membership_repository import MembershipSQLRepository
from adh6.member.storage.models import Membership as MembershipSQL


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.flush = AsyncMock()
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
            account_id=1,
            payment_method_id=1,
            create_at=datetime.now(),
        )
        mock_execute_result = MagicMock()
        mock_execute_result.all.return_value = [m_sql]
        mock_execute_result.scalars.return_value.all.return_value = [m_sql]
        mock_session.execute = AsyncMock(return_value=mock_execute_result)

        # When
        results, count = await membership_repo.search()

        # Then
        assert count == 1
        assert len(results) == 1
        assert results[0].status == MembershipStatus.COMPLETE.value

    async def test_create(self, membership_repo, mock_session):
        # Given
        body = SubscriptionBody(member=1, duration=12, account=1, paymentMethod=1)
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 0
        mock_session.execute = AsyncMock(return_value=mock_count_result)

        # When
        result = await membership_repo.create(body, MembershipStatus.COMPLETE)

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
            account_id=1,
            payment_method_id=1,
            create_at=datetime.now(),
        )
        mock_session.scalar = AsyncMock(return_value=m_sql)
        body = SubscriptionBody(duration=6)

        # When
        result = await membership_repo.update(u, body, MembershipStatus.COMPLETE)

        # Then
        assert m_sql.status == MembershipStatus.COMPLETE
        assert m_sql.duration == 6
        assert result.status == MembershipStatus.COMPLETE.value

    async def test_validate(self, membership_repo, mock_session):
        # Given
        u = str(uuid.uuid4())
        m_sql = MembershipSQL(uuid=u, status=MembershipStatus.PENDING_PAYMENT)
        mock_session.scalar = AsyncMock(return_value=m_sql)

        # When
        await membership_repo.validate(u)

        # Then
        assert m_sql.status == MembershipStatus.COMPLETE
