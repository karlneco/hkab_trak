import os
import logging
from functools import wraps
from flask_login import current_user

from flask import abort
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition
import base64
import requests  # SendGrid uses requests under the hood


# Create a logger
logger = logging.getLogger("hkabtrak")
logger.setLevel(logging.INFO)  # Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create a file handler
log_file = os.path.join(os.path.dirname(__file__), "hkabtrak.log")
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.WARNING)  # Logs warnings and errors to file

# Create a formatter and attach it to the handlers
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Attach handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

def send_email(to_emails, subject, body, cc=None, attachments=None):
    """
    Send an email using SendGrid API.

    :param to_emails: List of recipient email addresses.
    :param subject: Subject of the email.
    :param body: HTML body of the email.
    :param cc: List of CC email addresses (optional).
    :param attachments: List of tuples (filename, file_content, mime_type) for attachments.
    :return: Response status and message.
    """
    try:
        # Create a Mail object
        message = Mail(
            from_email=os.getenv("MAIL_DEFAULT_SENDER"),
            to_emails=to_emails if isinstance(to_emails, list) else [to_emails],
            subject=subject,
            html_content=body
        )

        # Add CC recipients if provided
        if cc:
            message.cc = [To(email) for email in (cc if isinstance(cc, list) else [cc])]

        # Attach files if provided
        if attachments:
            for filename, file_content, mime_type in attachments:
                encoded_content = base64.b64encode(file_content).decode()  # Encode attachment
                attachment = Attachment(
                    FileContent(encoded_content),
                    FileName(filename),
                    FileType(mime_type),
                    Disposition("attachment")
                )
                message.attachment = attachment

        # Send the email via SendGrid
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        logger.info(f"Email sent to {to_emails}: {response.status_code}")
        return response.status_code in [200, 202]

    except requests.exceptions.Timeout:
        logger.error("SendGrid request timed out. Email not sent.")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"SendGrid request failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending email: {e}")


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_type != 'A':
            abort(403)  # HTTP 403 Forbidden
        return f(*args, **kwargs)

    return decorated_function
