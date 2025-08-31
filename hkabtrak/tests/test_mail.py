import os
import unittest
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv

from hkabtrak.util import send_email  # Adjust if module path differs

# Load environment variables from .env
load_dotenv()


class TestSendEmail(unittest.TestCase):

    @patch("hkabtrak.util.sib_api_v3_sdk.TransactionalEmailsApi")
    def test_send_email_success(self, mock_brevo_client):
        """Test successful email sending"""

        # Mock response for a successful email send
        mock_response = MagicMock()
        mock_response.message_id = "mocked-message-id"
        mock_brevo_client.return_value.send_transac_email.return_value = mock_response

        result = send_email(
            to_emails=[os.getenv("TEST_EMAIL_TO")],
            subject="✅ Test Email Success",
            body="<p>This is a mocked successful test email.</p>"
        )

        self.assertTrue(result)
        mock_brevo_client.return_value.send_transac_email.assert_called_once()

    @patch("hkabtrak.util.sib_api_v3_sdk.TransactionalEmailsApi")
    def test_send_email_failure(self, mock_brevo_client):
        """Test email sending failure due to API error"""

        mock_brevo_client.return_value.send_transac_email.side_effect = Exception("Simulated API Error")

        result = send_email(
            to_emails=[os.getenv("TEST_EMAIL_TO")],
            subject="❌ Failure Test",
            body="<p>Simulated API error.</p>"
        )

        self.assertFalse(result)

    @patch("hkabtrak.util.sib_api_v3_sdk.TransactionalEmailsApi")
    def test_send_email_with_cc(self, mock_brevo_client):
        """Test email sending with CC"""

        mock_response = MagicMock()
        mock_response.message_id = "cc-test-id"
        mock_brevo_client.return_value.send_transac_email.return_value = mock_response

        result = send_email(
            to_emails=[os.getenv("TEST_EMAIL_TO")],
            subject="📬 CC Test",
            body="<p>Email with CC.</p>",
            cc=[os.getenv("TEST_EMAIL_CC")]
        )

        self.assertTrue(result)
        mock_brevo_client.return_value.send_transac_email.assert_called_once()

    @patch("hkabtrak.util.sib_api_v3_sdk.TransactionalEmailsApi")
    def test_send_email_with_attachment(self, mock_brevo_client):
        """Test email sending with an attachment"""

        mock_response = MagicMock()
        mock_response.message_id = "attachment-id"
        mock_brevo_client.return_value.send_transac_email.return_value = mock_response

        sample_attachment = ("test.txt", b"Sample file content", "text/plain")

        result = send_email(
            to_emails=[os.getenv("TEST_EMAIL_TO")],
            subject="📎 Attachment Test",
            body="<p>Email with file attached.</p>",
            attachments=[sample_attachment]
        )

        self.assertTrue(result)
        mock_brevo_client.return_value.send_transac_email.assert_called_once()

    def test_send_real_email(self):
        """
        Send a real email using live Brevo API key.
        This is not mocked — set TEST_EMAIL_TO in .env to use this.
        """
        to_email = os.getenv("TEST_EMAIL_TO")
        if not to_email:
            self.skipTest("TEST_EMAIL_TO not set in environment")

        result = send_email(
            to_emails=to_email,
            subject="📡 Real Brevo Email Test",
            body="<p>This is a real test from your app's Brevo integration.</p>"
        )

        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()