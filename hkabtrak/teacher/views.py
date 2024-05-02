from flask import Blueprint, render_template, request, redirect, url_for, flash
from hkabtrak.models import Class, load_user, User
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from hkabtrak import db

teachers_bp = Blueprint('teacher', __name__, template_folder='templates')


@teachers_bp.route('/teacher_register', methods=['GET', 'POST'])
@login_required
def teacher_register():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']
        name = request.form['name']
        class_name = request.form['class_name']

        if User.query.filter_by(email=username).first():
            return 'Email already registered'

        class_obj = Class.query.filter_by(name=class_name).first()

        if not class_obj:
            class_obj = Class(name=class_name)
            db.session.add(class_obj)
            # db.session.commit()

        # Check if there are any users in the user table
        existing_users = User.query.all()
        if not existing_users:
            # If no users exist, create the first user as an admin
            user_type = 'A'
        else:
            user_type = 'N'

        user = User(email=username, password=password, user_type=user_type, name=name)
        user.classes.append(class_obj)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('admin.teacher_list'))

    return render_template('teacher_register.html')


@teachers_bp.route('/teacher_view', methods=['GET', 'POST'])
@login_required
def teacher_view():
    user = load_user(current_user.get_id())
    classes = user.classes;
    return render_template('teacher_absences.html', teacher=user, classes=classes)


@teachers_bp.route('/teacher_login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(email=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Login Successful')
            if user.user_type == 'A':
                return redirect(url_for('admin.admin_main'))

            return redirect(url_for('teacher.teacher_view'))
        else:
            return 'Invalid username or password'

    return render_template('teacher_login.html')


@teachers_bp.route('/teacher_list')
@login_required
@login_required
def teacher_list():
    teachers = User.query.all()
    return render_template('teacher_list.html', teachers=teachers)


@teachers_bp.route('/edit_teacher/<int:teacher_id>', methods=['GET', 'POST'])
@login_required
def edit_teacher(teacher_id):
    teacher = User.query.get_or_404(teacher_id)
    if request.method == 'POST':
        teacher.username = request.form['username']
        teacher.class_teachers.class_name = request.form['class_name']
        db.session.commit()
        return redirect(url_for('teacher_list'))

    return render_template('edit_teacher.html', teacher=teacher)


@teachers_bp.route('/set_teacher_inactive/<int:teacher_id>')
@login_required
def set_teacher_inactive(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    teacher.is_active = False
    db.session.commit()
    return redirect(url_for('teacher_list'))


@teachers_bp.route('/teacher_logout')
@login_required
def teacher_logout():
    logout_user()
    return redirect(url_for('teacher_login'))
