import os
from functools import wraps

from flask import abort
from flask_login import current_user
from flask_mail import Message
from hkabtrak import mail


def send_email(subject, recipients, body, html_body=None):
    is_production = os.getenv('FLASK_ENV') == 'production'

    msg = Message(subject, recipients=recipients, body=body, html=html_body)
    if is_production:
        mail.send(msg)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_type != 'A':
            abort(403)  # HTTP 403 Forbidden
        return f(*args, **kwargs)

    return decorated_function
