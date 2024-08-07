from datetime import date, timedelta

from flask import Blueprint, render_template, request, redirect, url_for, flash, get_flashed_messages
from hkabtrak.models import Class, load_user, User, Absence
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from hkabtrak import db
from hkabtrak.util import send_email

staff_bp = Blueprint('staff', __name__, template_folder='templates')


@staff_bp.route('/staff_register', methods=['GET', 'POST'])
@login_required
def staff_register():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']
        name = request.form['name']

        if User.query.filter_by(email=username).first():
            return 'Email already registered'

        # Check if there are any users in the user table
        existing_users = User.query.all()
        if not existing_users:
            # If no users exist, create the first user as an admin
            user_type = 'A'
        else:
            user_type = 'N'

        user = User(email=username, password=password, user_type=user_type, name=name)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('admin.staff_list'))

    return render_template('staff_register.html')



@staff_bp.route('/staff_login', methods=['GET', 'POST'])
def staff_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(email=username).first()

        if user and user.check_password(password):
            login_user(user)
            current_user.type = user.user_type
            flash('Login Successful', category='success')
            if user.user_type == 'A':
                return redirect(url_for('admin.admin_main'))

            return redirect(url_for('absences.list'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    else:
        get_flashed_messages(with_categories=True)

    return render_template('staff_login.html')


@staff_bp.route('/staff_list')
@login_required
@login_required
def staff_list():
    staff = User.query.all()
    return render_template('staff_list.html', staff=staff)


@staff_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'danger')
        elif new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
        else:
            # Update the user's password
            current_user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            flash('Your password has been updated!', 'success')

            # Send email notification
            send_email(
                subject="Your Password Has Been Changed",
                recipients=[current_user.email],
                body="Hello, your password has been successfully updated. If you did not make this change, please contact support immediately.",
                html_body=render_template('password_changed.html')
            )
            return redirect(url_for('staff.profile'))

    return render_template('profile.html')


@staff_bp.route('/set_staff_inactive/<int:staff_id>')
@login_required
def set_staff_inactive(staff_id):
    staff = User.query.get_or_404(staff_id)
    staff.is_active = False
    db.session.commit()
    return redirect(url_for('staff_list'))


@staff_bp.route('/staff_logout')
@login_required
def staff_logout():
    logout_user()
    return redirect(url_for('staff.staff_login'))
