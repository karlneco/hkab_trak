from datetime import date, timedelta, datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, get_flashed_messages
from sqlalchemy.exc import IntegrityError

from hkabtrak.models import Class, load_user, User, Absence, Semester
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from hkabtrak import db

semester_bp = Blueprint('semester', __name__, template_folder='templates')


@semester_bp.route('/list', methods=['GET'])
@login_required
def semester_list():
    semesters = Semester.query.order_by(Semester.start_date.desc()).all()
    return render_template('semester_list.html', semesters=semesters)


@semester_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date and/or time format.', 'danger')
            return redirect(url_for('semester.create'))

        try:
            # Create a new Semester instance
            new_semester = Semester(name=name, start_date=start_date, end_date=end_date)
            db.session.add(new_semester)
            db.session.commit()

            flash('Semester created successfully!', 'success')
            return redirect(url_for('semester.semester_list'))
        except IntegrityError:
            db.session.rollback()  # Roll back the transaction so you can continue using the session
            flash('A semester with that name already exists. Please use a different name.', 'danger')
            return render_template('semester_create.html')

    return render_template('semester_create.html')


@semester_bp.route('/edit/<int:semester_id>', methods=['GET', 'POST'])
@login_required
def edit(semester_id):
    semester = Semester.query.get_or_404(semester_id)

    if request.method == 'POST':
        semester.name = request.form['name']
        start_date_str = request.form['start_date']
        end_date_str = request.form['end_date']
        semester.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        semester.end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        db.session.commit()
        flash('Semester updated successfully!', 'success')
        return redirect(url_for('semester.semester_list'))

    return render_template('semester_edit.html', semester=semester)


@semester_bp.route('/delete/<int:semester_id>', methods=['GET', 'POST'])
@login_required
def delete(semester_id):
    semester = Semester.query.get_or_404(semester_id)
    db.session.delete(semester)
    db.session.commit()
    flash('Semester deleted successfully!', 'info')
    return redirect(url_for('semester.semester_list'))
