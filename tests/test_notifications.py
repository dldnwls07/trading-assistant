# tests/test_notifications.py
import os
import smtplib
import unittest
from unittest.mock import MagicMock, patch

from trading_assist.notifications import send_email


class TestNotifications(unittest.TestCase):

    @patch.dict(
        os.environ,
        {
            "SMTP_SERVER": "smtp.test.com",
            "SMTP_PORT": "587",
            "SMTP_USER": "user@test.com",
            "SMTP_PASSWORD": "password",  # pragma: allowlist secret
        },
    )
    @patch("smtplib.SMTP")
    def test_send_email_success(self, mock_smtp):
        """
        Tests successful email sending.
        """
        # Arrange
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        subject = "Test Subject"
        body = "Test Body"
        to_email = "recipient@example.com"

        # Act
        result = send_email(subject, body, to_email)

        # Assert
        self.assertTrue(result)
        mock_smtp.assert_called_with("smtp.test.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_with("user@test.com", "password")
        mock_server.send_message.assert_called_once()

        # Check email content
        sent_msg = mock_server.send_message.call_args[0][0]
        self.assertEqual(sent_msg["Subject"], subject)
        self.assertEqual(sent_msg["To"], to_email)
        self.assertEqual(sent_msg["From"], "user@test.com")
        # For MIMEMultipart, get the payload from the first part
        self.assertEqual(
            sent_msg.get_payload(0).get_payload(decode=True).decode(), body
        )

    def test_send_email_missing_env_vars(self):
        """
        Tests that email sending fails if environment variables are missing.
        """
        # Arrange - ensure env vars are not set
        with patch.dict(os.environ, {}, clear=True):
            # Act
            result = send_email("S", "B", "E")
            # Assert
            self.assertFalse(result)

    @patch.dict(
        os.environ,
        {
            "SMTP_SERVER": "smtp.test.com",
            "SMTP_PORT": "587",
            "SMTP_USER": "user@test.com",
            "SMTP_PASSWORD": "wrong_password",  # pragma: allowlist secret
        },
    )
    @patch("smtplib.SMTP")
    def test_send_email_auth_error(self, mock_smtp):
        """
        Tests handling of SMTPAuthenticationError.
        """
        # Arrange
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(
            535, b"Authentication failed"
        )

        # Act
        result = send_email("S", "B", "E")

        # Assert
        self.assertFalse(result)
        mock_server.login.assert_called_once()


if __name__ == "__main__":
    unittest.main()
