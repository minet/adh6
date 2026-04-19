from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.exceptions import TemplateNotFoundError, UndecalredVariableInTemplate
from adh6.member.interfaces import NotificationRepository, NotificationTemplateRepository
from adh6.member.notification_manager import NotificationManager


@pytest.fixture
def mock_notification_repository():
    return MagicMock(spec=NotificationRepository)


@pytest.fixture
def mock_template_repository():
    return MagicMock(spec=NotificationTemplateRepository)


@pytest.fixture
def notification_manager(mock_notification_repository, mock_template_repository):
    return NotificationManager(
        notification_repository=mock_notification_repository, notification_template_repository=mock_template_repository
    )


class TestSend:
    async def test_happy_path(self, notification_manager, mock_template_repository, mock_notification_repository):
        # Given
        template_title = "Welcome"
        member_email = "test@example.com"
        template_content = "Hello {{ name }}!"
        mock_template = MagicMock()
        mock_template.template = template_content
        mock_template_repository.get = AsyncMock(return_value=mock_template)
        mock_notification_repository.send = AsyncMock()

        # When
        await notification_manager.send(template_title, member_email, name="John")

        # Then
        mock_notification_repository.send.assert_called_once_with(member_email, template_title, "Hello John!")

    async def test_template_not_found(self, notification_manager, mock_template_repository):
        # Given
        mock_template_repository.get = AsyncMock(return_value=None)

        # When / Then
        with pytest.raises(TemplateNotFoundError):
            await notification_manager.send("Unknown", "test@example.com")

    async def test_undeclared_variable(self, notification_manager, mock_template_repository):
        # Given
        template_content = "Hello {{ name }}!"
        mock_template = MagicMock()
        mock_template.template = template_content
        mock_template_repository.get = AsyncMock(return_value=mock_template)

        # When / Then (missing 'name' parameter)
        with pytest.raises(UndecalredVariableInTemplate):
            await notification_manager.send("Welcome", "test@example.com")

    async def test_extra_variable(self, notification_manager, mock_template_repository):
        # Given
        template_content = "Hello {{ name }}!"
        mock_template = MagicMock()
        mock_template.template = template_content
        mock_template_repository.get = AsyncMock(return_value=mock_template)

        # When / Then (extra 'age' parameter)
        with pytest.raises(UndecalredVariableInTemplate):
            await notification_manager.send("Welcome", "test@example.com", name="John", age=30)
