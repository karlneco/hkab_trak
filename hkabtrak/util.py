import os
import logging
from functools import wraps
from flask_login import current_user
from flask import abort

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from sib_api_v3_sdk.models import SendSmtpEmail, SendSmtpEmailTo, SendSmtpEmailCc, SendSmtpEmailAttachment

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

# Setup Brevo API configuration
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")


def send_email(to_emails, subject, body, cc=None, attachments=None):
    """
    Send an email using Brevo (Sendinblue) transactional email API.
    """
    try:
        api_client = sib_api_v3_sdk.ApiClient(configuration)
        print("default headers=", api_client.default_headers)
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(api_client)

        # Convert recipients
        to = [SendSmtpEmailTo(email=email) for email in (to_emails if isinstance(to_emails, list) else [to_emails])]
        cc_list = [SendSmtpEmailCc(email=email) for email in (cc if isinstance(cc, list) else [cc])] if cc else None

        # Convert attachments
        brevo_attachments = []
        if attachments:
            for filename, file_content, mime_type in attachments:
                encoded_content = base64.b64encode(file_content).decode()
                brevo_attachments.append(
                    SendSmtpEmailAttachment(
                        name=filename,
                        content=encoded_content
                    )
                )

        email = SendSmtpEmail(
            to=to,
            cc=cc_list,
            subject=subject,
            html_content=body,
            sender={"email": os.getenv("MAIL_DEFAULT_SENDER")},
            attachment=brevo_attachments if brevo_attachments else None
        )

        # Send the email
        result = api_instance.send_transac_email(email)
        logger.info(f"Email sent to {to_emails}: Message ID {result.message_id}")
        return True

    except ApiException as e:
        logger.error(f"Brevo API exception: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending email: {e}")
        return False


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_type != 'A':
            abort(403)  # HTTP 403 Forbidden
        return f(*args, **kwargs)

    return decorated_function
