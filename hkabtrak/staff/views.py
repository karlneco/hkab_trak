from flask import Blueprint, render_template, request, redirect, url_for, flash
from hkabtrak.models import Class, load_user, User
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from hkabtrak import db

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


@staff_bp.route('/staff_view', methods=['GET', 'POST'])
@login_required
def staff_view():
    user = load_user(current_user.get_id())
    classes = user.classes;
    return render_template('staff_absences.html', staff=user, classes=classes)


@staff_bp.route('/staff_login', methods=['GET', 'POST'])
def staff_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(email=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Login Successful')
            if user.user_type == 'A':
                return redirect(url_for('admin.admin_main'))

            return redirect(url_for('staff.staff_view'))
        else:
            return 'Invalid username or password'

    return render_template('staff_login.html')


@staff_bp.route('/staff_list')
@login_required
@login_required
def staff_list():
    staff = User.query.all()
    return render_template('staff_list.html', staff=staff)


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
