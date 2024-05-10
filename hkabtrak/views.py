from hkabtrak import db
from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, get_flashed_messages
from hkabtrak.models import Class, load_user, User, Absence
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template, request, redirect, url_for, flash, Blueprint
from hkabtrak.models import Class, Absence


valid_reasons = ['Absent', 'Late', 'Leaving Early', 'Absent for a Time', '欠席', '遅刻', '早退', '時間で欠席']

root_bp = Blueprint('root', __name__, template_folder='templates')

@root_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        parent_email = request.form['parent_email']
        class_id = request.form['class_id']
        student_name = request.form['student_name']
        reason = request.form['reason']
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        comment = request.form['comment']

        date_str = request.form.get('date')
        try:
            absence_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_time_str, '%H:%M').time() if start_time_str else None
            end_time = datetime.strptime(end_time_str, '%H:%M').time() if end_time_str else None
            print("Parsed date:", absence_date)  # Debugging line
        except ValueError:
            flash('Invalid date and/or time format.', 'error')
            return redirect(url_for('submit_absence'))

        # Validate date is not in the past
        today = date.today()
        if absence_date < today:
            flash('The date cannot be in the past.', 'error')
            return redirect(url_for('submit_absence'))

        # Validate email format (simple check)
        if '@' not in parent_email or '.' not in parent_email.split('@')[-1]:
            flash('Invalid email format.', 'error')
            return redirect(url_for('submit_absence'))

        # Validate reason
        if reason not in valid_reasons:
            flash('Invalid reason for absence.', 'error')
            return redirect(url_for('submit_absence'))

        # Additional validation based on reason
        if reason == "Late" and not start_time:
            flash('Expected time is required for "Late".', 'error')
            return redirect(url_for('submit_absence'))
        if reason == "Leaving Early" and not end_time:
            flash('Leaving time is required for "Leaving Early".', 'error')
            return redirect(url_for('submit_absence'))
        if reason == "Absent for a Time" and (not start_time or not end_time):
            flash('Both leaving and return times are required for "Absent for a Time".', 'error')
            return redirect(url_for('submit_absence'))

        absence = Absence(student_name=student_name, reason=reason, class_id=class_id, date=absence_date,
                          start_time=start_time, end_time=end_time, parent_email=parent_email, comment=comment)
        db.session.add(absence)
        db.session.commit()

        return redirect(url_for('root.thank_you'))
    else:
        get_flashed_messages(with_categories=True)

    classes = Class.query.all()
    today = datetime.today().strftime('%Y-%m-%d')
    return render_template('new_absence.html', classes=classes, today=today)


@root_bp.route('/thank_you')
def thank_you():
    return render_template('absence_submited.html')
