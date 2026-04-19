from unittest.mock import MagicMock, patch

from adh6.member.smtp.notification_repository import NotificationSMTPRepository


class TestSend:
    def test_send_happy_path(self, monkeypatch):
        # Given
        repo = NotificationSMTPRepository()
        recipient = "test@example.com"
        subject = "Welcome"
        body = "Hello John!"

        mock_current_app = MagicMock()
        mock_current_app.config = {"SMTP_SERVER": "localhost"}
        monkeypatch.setattr("adh6.member.smtp.notification_repository.current_app", mock_current_app)

        with patch("smtplib.SMTP") as mock_smtp:
            mock_server = mock_smtp.return_value
            # When
            repo.send(recipient, subject, body)

            # Then
            mock_smtp.assert_called_once_with("localhost", 25)
            mock_server.send_message.assert_called_once()
            msg = mock_server.send_message.call_args[0][0]
            assert msg["Subject"] == subject
            assert msg["To"] in ["MiNET <test@example.com>", 'MiNET <"test@example.com">']

    def test_send_no_smtp(self, monkeypatch):
        # Given
        repo = NotificationSMTPRepository()
        mock_current_app = MagicMock()
        mock_current_app.config = {"SMTP_SERVER": None}
        monkeypatch.setattr("adh6.member.smtp.notification_repository.current_app", mock_current_app)

        with patch("smtplib.SMTP") as mock_smtp:
            # When
            repo.send("any", "any", "any")

            # Then
            mock_smtp.assert_not_called()
