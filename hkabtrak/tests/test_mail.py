import os
import unittest
from unittest.mock import patch, MagicMock
from hkabtrak.util import send_email

class TestSendEmail(unittest.TestCase):

    @patch("hkabtrak.util.SendGridAPIClient")
    def test_send_email_success(self, mock_sendgrid_client):
        """Test successful email sending"""

        # Mock response for a successful email send
        mock_response = MagicMock()
        mock_response.status_code = 202  # SendGrid returns 202 for success
        mock_sendgrid_client.return_value.send.return_value = mock_response

        # Call the function
        result = send_email(
            to_emails=["test@example.com"],
            subject="Test Subject",
            body="<p>This is a test email.</p>"
        )

        # Assertions
        self.assertTrue(result)  # Function should return True on success
        mock_sendgrid_client.return_value.send.assert_called_once()  # Ensure send() was called

    @patch("hkabtrak.util.SendGridAPIClient")
    def test_send_email_failure(self, mock_sendgrid_client):
        """Test email sending failure due to API error"""

        # Mock response for a failed email send
        mock_sendgrid_client.return_value.send.side_effect = Exception("API Error")

        # Call the function
        result = send_email(
            to_emails=["test@example.com"],
            subject="Test Subject",
            body="<p>This is a test email.</p>"
        )

        # Assertions
        self.assertFalse(result)  # Function should return False on failure

    @patch("hkabtrak.util.SendGridAPIClient")
    def test_send_email_timeout(self, mock_sendgrid_client):
        """Test email sending timeout"""

        # Simulate a timeout exception
        mock_sendgrid_client.return_value.send.side_effect = TimeoutError("Request Timeout")

        # Call the function
        result = send_email(
            to_emails=["test@example.com"],
            subject="Test Subject",
            body="<p>This is a test email.</p>"
        )

        # Assertions
        self.assertFalse(result)  # Function should return False on timeout

    @patch("hkabtrak.util.SendGridAPIClient")
    def test_send_email_with_cc(self, mock_sendgrid_client):
        """Test email sending with CC recipients"""

        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_sendgrid_client.return_value.send.return_value = mock_response

        # Call the function with CC
        result = send_email(
            to_emails=["recipient@example.com"],
            subject="CC Test Email",
            body="<p>Testing CC.</p>",
            cc=["cc@example.com"]
        )

        # Assertions
        self.assertTrue(result)
        mock_sendgrid_client.return_value.send.assert_called_once()

    @patch("hkabtrak.util.SendGridAPIClient")
    def test_send_email_with_attachment(self, mock_sendgrid_client):
        """Test email sending with an attachment"""

        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_sendgrid_client.return_value.send.return_value = mock_response

        # Simulate a file attachment
        sample_attachment = ("test.txt", b"Hello, world!", "text/plain")

        # Call the function with an attachment
        result = send_email(
            to_emails=["recipient@example.com"],
            subject="Attachment Test",
            body="<p>Testing attachment.</p>",
            attachments=[sample_attachment]
        )

        # Assertions
        self.assertTrue(result)
        mock_sendgrid_client.return_value.send.assert_called_once()

if __name__ == "__main__":
    unittest.main()