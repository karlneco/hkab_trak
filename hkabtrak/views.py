from hkabtrak import db
from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, get_flashed_messages

from hkabtrak.absence_form import AbsenceForm
from hkabtrak.models import Class, load_user, User, Absence
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template, request, redirect, url_for, flash, Blueprint
from hkabtrak.models import Class, Absence
from flask_mail import Message
from hkabtrak import mail

valid_reasons = ['Absent', 'Late', 'Leaving Early', 'Absent for a Time', '欠席', '遅刻', '早退', '時間で欠席']

root_bp = Blueprint('root', __name__, template_folder='templates')


@root_bp.route('/', methods=['GET', 'POST'])
def index():
    form = AbsenceForm()
    default_course_choice = [('', '学年を選択してください')]
    form.class_id.choices = default_course_choice + [
        (cls.id, cls.name, {'data-instructions': cls.instructions or 'None'}) for cls in Class.query.all()
    ]

    classes = Class.query.all()
    today = datetime.today().strftime('%Y-%m-%d')
    return render_template('new_absence.html', form=form, today=today)


@root_bp.route('/thank_you')
def thank_you():
    return render_template('absence_submited.html')


def send_absence_notification(recipients, student_name, reason, absence_date, start_time, end_time, comment):
    """
    Send email notifications to the specified recipients about the student's absence.
    """
    subject = "nameさんの欠席連絡受領のお知らせ_2024_06_24"
    body = render_template(
        'email/absence_notification.html',
        student_name=student_name,
        reason=reason,
        date=absence_date,
        start_time=start_time,
        end_time=end_time,
        comment=comment
    )
    msg = Message(subject, recipients=recipients, html=body)
    mail.send(msg)
