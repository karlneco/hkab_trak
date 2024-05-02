from flask import Blueprint, render_template, request, redirect, url_for, flash
from hkabtrak.models import Class, load_course, User
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from hkabtrak import db

courses_bp = Blueprint('course', __name__, template_folder='templates')


@courses_bp.route('/course_create', methods=['GET', 'POST'])
@login_required
def course_create():
    if request.method == 'POST':
        name = request.form['name']

        class_obj = Class(name=name)
        db.session.add(class_obj)
        db.session.commit()
        return redirect(url_for('admin.course_list'))

    return render_template('course_create.html')


@courses_bp.route('/course_view', methods=['GET', 'POST'])
@login_required
def course_view():
    course = load_course()
    return render_template('course_edit.html', course=course)


@courses_bp.route('/course_list')
@login_required
def course_list():
    classes = Class.query.all()
    return render_template('course_list.html', classes=classes)


@courses_bp.route('/edit_course/<int:course_id>', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    course = Class.query.get_or_404(course_id)
    if request.method == 'POST':
        course.name = request.form['name']
        db.session.commit()
        return redirect(url_for('course_list'))

    return render_template('edit_course.html', course=course)