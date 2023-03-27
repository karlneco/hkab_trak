from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from hkabtrak.models import Absence, Class
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from hkabtrak import db

absences_bp = Blueprint('absences', __name__, template_folder='templates')


@absences_bp.route('/absences')
@absences_bp.route('/submit_absence', methods=['GET', 'POST'])
def submit_absence():
    if request.method == 'POST':
        student_name = request.form['student_name']
        reason = request.form['reason']
        class_id = request.form['class_id']
        date_str = request.form['date']

        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

        absence = Absence(student_name=student_name, reason=reason, class_id=class_id, date=date_obj)
        db.session.add(absence)
        db.session.commit()

        flash('Absence submitted successfully', 'success')
        return redirect(url_for('absences.submit_absence'))

    classes = Class.query.all()
    today = datetime.today().strftime('%Y-%m-%d')
    return render_template('new_absence.html', classes=classes, today=today)


@absences_bp.route('/all_absences')
@login_required
def all_absences():
    absences = Absence.query.join(Class).order_by(Absence.date.desc()).all()
    return render_template('all_absences.html', absences=absences)


