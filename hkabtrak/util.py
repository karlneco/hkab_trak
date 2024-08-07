from flask_mail import Message
from hkabtrak import mail


def send_email(subject, recipients, body, html_body=None):
    msg = Message(subject, recipients=recipients, body=body, html=html_body)
    mail.send(msg)
